from io import BytesIO, StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from apps.catalog.models import Category, Company, Product
from apps.core.forms import CustomerRegistrationForm
from apps.promotions.models import Promotion
from apps.core.models import DeliveryArea
from apps.core.management.commands.optimize_images import get_optimized_image_fields
from media.utils.image_optimizer import optimize_image_file


def make_image_bytes(
    image_format="JPEG",
    size=(1600, 900),
    mode="RGB",
    color="red",
    *,
    exif=None,
):
    output = BytesIO()
    image = Image.new(mode, size, color=color)
    save_kwargs = {"exif": exif} if exif is not None else {}
    image.save(output, format=image_format, **save_kwargs)
    return output.getvalue()


class CustomerRegistrationFormTests(TestCase):
    def setUp(self):
        self.area = DeliveryArea.objects.create(name="Damascus")

    def test_name_fields_come_before_phone_and_password_fields(self):
        form = CustomerRegistrationForm(language="en")

        self.assertEqual(
            list(form.fields)[:6],
            ["name", "father_name", "last_name", "username", "password1", "password2"],
        )
        self.assertNotIn("autofocus", form.fields["username"].widget.attrs)

    def test_registration_combines_name_parts_for_existing_profile_contract(self):
        form = CustomerRegistrationForm(
            data={
                "name": "Ahmad",
                "father_name": "Mahmoud",
                "last_name": "Saleh",
                "username": "944444444",
                "password1": "secure-pass-2026",
                "password2": "secure-pass-2026",
                "area": self.area.pk,
                "sub_area": "",
                "street_address": "Main street",
                "building": "",
                "floor": "",
                "apartment": "",
                "nearby_landmark": "",
                "notes": "",
            },
            language="en",
        )

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertEqual(user.first_name, "Ahmad Mahmoud Saleh")
        self.assertEqual(user.customer_profile.full_name, "Ahmad Mahmoud Saleh")


class ImageOptimizerUtilityTests(TestCase):
    def test_exif_rotation_is_applied(self):
        exif = Image.Exif()
        exif[274] = 6
        content = make_image_bytes(size=(40, 20), exif=exif)

        result = optimize_image_file(
            BytesIO(content),
            "rotated.jpg",
            max_dimension=100,
            quality=80,
        )

        self.assertEqual(result.filename, "rotated.webp")
        self.assertEqual(result.original_dimensions, (40, 20))
        self.assertEqual(result.optimized_dimensions, (20, 40))

    def test_png_transparency_is_preserved(self):
        content = make_image_bytes(
            image_format="PNG",
            size=(20, 20),
            mode="RGBA",
            color=(255, 0, 0, 0),
        )

        result = optimize_image_file(
            BytesIO(content),
            "transparent.png",
            max_dimension=100,
            quality=85,
        )

        with Image.open(BytesIO(result.content)) as image:
            self.assertEqual(image.format, "WEBP")
            self.assertEqual(image.mode, "RGBA")
            self.assertEqual(image.getpixel((0, 0))[3], 0)


class AutomaticImageOptimizationTests(TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.media_root = Path(self.temporary_directory.name)
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    def test_product_upload_is_saved_only_as_resized_webp(self):
        category = Category.objects.create(name="Food")
        product = Product.objects.create(
            category=category,
            name="Large Product",
            price=100,
            primary_image=SimpleUploadedFile(
                "large.jpg",
                make_image_bytes(size=(1600, 900)),
                content_type="image/jpeg",
            ),
        )

        self.assertTrue(product.primary_image.name.endswith(".webp"))
        self.assertFalse((self.media_root / "products" / "large.jpg").exists())
        with Image.open(product.primary_image.path) as image:
            self.assertEqual(image.format, "WEBP")
            self.assertLessEqual(max(image.size), 800)

    def test_each_model_uses_its_configured_profile(self):
        category = Category.objects.create(
            name="Category",
            cover_image=SimpleUploadedFile(
                "category.png",
                make_image_bytes("PNG", size=(1800, 1200)),
                content_type="image/png",
            ),
        )
        company = Company.objects.create(
            code="company-1",
            name="Company",
            logo=SimpleUploadedFile(
                "logo.png",
                make_image_bytes("PNG", size=(1200, 700)),
                content_type="image/png",
            ),
        )
        promotion = Promotion.objects.create(
            title="Banner",
            image=SimpleUploadedFile(
                "banner.jpg",
                make_image_bytes(size=(2200, 1000)),
                content_type="image/jpeg",
            ),
        )

        for field_file, max_dimension in (
            (category.cover_image, 1000),
            (company.logo, 500),
            (promotion.image, 1400),
        ):
            self.assertTrue(field_file.name.endswith(".webp"))
            with Image.open(field_file.path) as image:
                self.assertLessEqual(max(image.size), max_dimension)

    def test_direct_field_file_save_is_optimized_before_storage(self):
        category = Category.objects.create(name="Food")
        product = Product.objects.create(
            category=category,
            name="Direct Save",
            price=100,
        )

        product.primary_image.save(
            "direct.png",
            ContentFile(make_image_bytes("PNG", size=(1000, 500))),
        )

        self.assertTrue(product.primary_image.name.endswith(".webp"))
        self.assertFalse((self.media_root / "products" / "direct.png").exists())

    def test_all_project_image_fields_are_registered(self):
        registered = {
            (model._meta.label, field.name)
            for model, field in get_optimized_image_fields()
        }

        self.assertEqual(
            registered,
            {
                ("catalog.Category", "cover_image"),
                ("catalog.Company", "logo"),
                ("catalog.Product", "primary_image"),
                ("catalog.ProductImage", "image"),
                ("promotions.Promotion", "image"),
            },
        )


class OptimizeImagesCommandTests(TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.media_root = Path(self.temporary_directory.name)
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.category = Category.objects.create(name="Food")

    def create_legacy_product_image(self, sku, filename):
        product = Product.objects.create(
            category=self.category,
            name=f"Product {sku}",
            price=100,
            sku=sku,
        )
        storage = Product._meta.get_field("primary_image").storage
        old_name = storage.save(
            f"products/{filename}",
            ContentFile(make_image_bytes(size=(1200, 700))),
        )
        Product.objects.filter(pk=product.pk).update(primary_image=old_name)
        product.refresh_from_db()
        return product, old_name

    def test_dry_run_does_not_change_file_or_database(self):
        product, old_name = self.create_legacy_product_image("P-1", "legacy.jpg")
        output = StringIO()

        call_command("optimize_images", "--dry-run", stdout=output)

        product.refresh_from_db()
        self.assertEqual(product.primary_image.name, old_name)
        self.assertTrue(product.primary_image.storage.exists(old_name))
        self.assertIn("Would optimize: 1", output.getvalue())

    def test_command_updates_path_deletes_original_and_honors_limit(self):
        first, first_old_name = self.create_legacy_product_image("P-1", "first.jpg")
        second, second_old_name = self.create_legacy_product_image("P-2", "second.jpg")

        call_command("optimize_images", "--limit", "1", stdout=StringIO())

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertTrue(first.primary_image.name.endswith(".webp"))
        self.assertFalse(first.primary_image.storage.exists(first_old_name))
        self.assertTrue(first.primary_image.storage.exists(first.primary_image.name))
        self.assertEqual(second.primary_image.name, second_old_name)
        self.assertTrue(second.primary_image.storage.exists(second_old_name))

        call_command("optimize_images", "--limit", "1", stdout=StringIO())

        second.refresh_from_db()
        self.assertTrue(second.primary_image.name.endswith(".webp"))
        self.assertFalse(second.primary_image.storage.exists(second_old_name))

    def test_missing_file_is_skipped_without_crashing(self):
        product = Product.objects.create(
            category=self.category,
            name="Missing",
            price=100,
            sku="P-MISSING",
        )
        Product.objects.filter(pk=product.pk).update(
            primary_image="products/missing.jpg"
        )
        output = StringIO()

        call_command("optimize_images", stdout=output)

        self.assertIn("Skipped: 1", output.getvalue())
        self.assertIn("Failed: 0", output.getvalue())

    def test_bad_image_failure_does_not_stop_later_records(self):
        bad_product = Product.objects.create(
            category=self.category,
            name="Bad",
            price=100,
            sku="P-BAD",
        )
        storage = Product._meta.get_field("primary_image").storage
        bad_name = storage.save(
            "products/bad.jpg",
            ContentFile(b"not-an-image"),
        )
        Product.objects.filter(pk=bad_product.pk).update(primary_image=bad_name)
        good_product, good_old_name = self.create_legacy_product_image(
            "P-GOOD",
            "good.jpg",
        )
        output = StringIO()
        errors = StringIO()

        call_command("optimize_images", stdout=output, stderr=errors)

        good_product.refresh_from_db()
        self.assertTrue(good_product.primary_image.name.endswith(".webp"))
        self.assertFalse(storage.exists(good_old_name))
        self.assertIn("Failed: 1", output.getvalue())
        self.assertIn("Failed", errors.getvalue())
