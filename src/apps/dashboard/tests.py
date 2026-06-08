from decimal import Decimal
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import TestCase, override_settings
from openpyxl import Workbook
from PIL import Image

from apps.catalog.models import (
    Category,
    Company,
    Product,
    ProductCompany,
    ProductCompanyOption,
)

from .views import (
    CATEGORY_IMAGE_EXCEL_HEADERS,
    PRODUCT_COMPANY_EXCEL_HEADERS,
    PRODUCT_COMPANY_OPTION_EXCEL_HEADERS,
    PRODUCT_EXCEL_HEADERS,
    import_product_excel_rows,
    load_excel_image,
    validate_product_excel_workbook,
)


class CompanyExcelImportTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Shoes", slug="shoes")

    def import_rows(self, logo_url, company_name="Company One"):
        return import_product_excel_rows(
            {
                "products": [
                    {
                        "category": self.category,
                        "name": "Running Shoes",
                        "short_description": "",
                        "description": "",
                        "price": Decimal("0"),
                        "product_type": Product.PRODUCT_TYPE_COMPANY_GROUPED,
                        "price_link_mode": Product.BEHAVIOR_INHERIT,
                        "is_price_linked_to_dollar": False,
                        "sold_by_weight_mode": Product.BEHAVIOR_INHERIT,
                        "sold_by_weight": False,
                        "has_options": False,
                        "unit_label": "piece",
                        "is_available": True,
                        "is_featured": False,
                        "external_image_url": "",
                        "sku": "SHOES-001",
                        "_import_keys": [("sku", "shoes-001")],
                    }
                ],
                "options": [],
                "companies": [
                    {
                        "company_id": "Com-1",
                        "name": company_name,
                        "external_logo_url": logo_url,
                        "order": 2,
                        "is_active": True,
                    }
                ],
                "company_options": [
                    {
                        "product_key": ("sku", "shoes-001"),
                        "company_id": "Com-1",
                        "name": "Size 42",
                        "price": Decimal("15.50"),
                        "is_available": True,
                        "order": 0,
                    }
                ],
            }
        )

    def test_company_is_shared_and_updated_by_stable_company_id(self):
        self.import_rows("https://example.com/old-logo.png")
        first_company = Company.objects.get(code="Com-1")
        product_company = ProductCompany.objects.select_related("company").get()
        second_product = Product.objects.create(
            category=self.category,
            name="Walking Shoes",
            product_type=Product.PRODUCT_TYPE_COMPANY_GROUPED,
            price=Decimal("0"),
            sku="SHOES-002",
        )
        second_product_company = ProductCompany.objects.create(
            product=second_product,
            company=first_company,
        )

        self.import_rows(
            "https://example.com/new-logo.png",
            company_name="Updated Company",
        )

        first_company.refresh_from_db()
        product_company.refresh_from_db()
        second_product_company.refresh_from_db()
        self.assertEqual(Company.objects.filter(code__iexact="Com-1").count(), 1)
        self.assertEqual(ProductCompany.objects.count(), 2)
        self.assertEqual(product_company.company_id, first_company.id)
        self.assertEqual(second_product_company.company_id, first_company.id)
        self.assertEqual(first_company.name, "Updated Company")
        self.assertEqual(
            first_company.external_logo_url,
            "https://example.com/new-logo.png",
        )
        self.assertEqual(product_company.company.external_logo_url, first_company.external_logo_url)
        self.assertEqual(
            second_product_company.company.external_logo_url,
            first_company.external_logo_url,
        )

    def test_empty_logo_url_uses_no_per_product_logo_copy(self):
        self.import_rows("")

        company = Company.objects.get(code="Com-1")
        product_company = ProductCompany.objects.select_related("company").get()
        self.assertFalse(company.logo)
        self.assertEqual(company.external_logo_url, "")
        self.assertFalse(hasattr(product_company, "logo_id"))

    def test_import_merges_matching_legacy_company_instead_of_duplicating_it(self):
        product = Product.objects.create(
            category=self.category,
            name="Running Shoes",
            product_type=Product.PRODUCT_TYPE_COMPANY_GROUPED,
            price=Decimal("0"),
            sku="SHOES-001",
        )
        legacy_company = Company.objects.create(
            code="legacy-1",
            name="Company One",
        )
        legacy_relation = ProductCompany.objects.create(
            product=product,
            company=legacy_company,
        )
        ProductCompanyOption.objects.create(
            company=legacy_relation,
            name="Size 42",
            price=Decimal("14.00"),
        )

        self.import_rows("https://example.com/new-logo.png")

        canonical_company = Company.objects.get(code="Com-1")
        relation = ProductCompany.objects.get(
            product=product,
            company=canonical_company,
        )
        self.assertFalse(Company.objects.filter(code__startswith="legacy-").exists())
        self.assertEqual(ProductCompany.objects.filter(product=product).count(), 1)
        self.assertEqual(relation.options.count(), 1)
        self.assertEqual(relation.options.get().price, Decimal("15.50"))


class ExcelImageImportTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Footwear", slug="shoes")

    @staticmethod
    def png_bytes():
        output = BytesIO()
        Image.new("RGB", (2, 2), color="red").save(output, format="PNG")
        return output.getvalue()

    @staticmethod
    def append_dict_row(worksheet, headers, values):
        worksheet.append([values.get(header, "") for header in headers])

    def build_workbook(self, image_value, external_url=""):
        workbook = Workbook()
        products_sheet = workbook.active
        products_sheet.title = "Products"
        products_sheet.append(PRODUCT_EXCEL_HEADERS)
        self.append_dict_row(
            products_sheet,
            PRODUCT_EXCEL_HEADERS,
            {
                "product_name": "Running Shoes",
                "category": "shoes",
                "price": "15.50",
                "product_type": "company_grouped",
                "image": image_value,
                "external_image_url": external_url,
                "sku": "SHOES-001",
                "is_available": "true",
            },
        )

        companies_sheet = workbook.create_sheet("Companies")
        companies_sheet.append(PRODUCT_COMPANY_EXCEL_HEADERS)
        self.append_dict_row(
            companies_sheet,
            PRODUCT_COMPANY_EXCEL_HEADERS,
            {
                "company_id": "Com-1",
                "company_name": "Company One",
                "logo": image_value,
                "external_logo_url": external_url,
                "is_active": "true",
            },
        )

        company_options_sheet = workbook.create_sheet("CompanyOptions")
        company_options_sheet.append(PRODUCT_COMPANY_OPTION_EXCEL_HEADERS)
        self.append_dict_row(
            company_options_sheet,
            PRODUCT_COMPANY_OPTION_EXCEL_HEADERS,
            {
                "product_sku": "SHOES-001",
                "company_id": "Com-1",
                "option_name": "Size 42",
                "price": "15.50",
                "is_available": "true",
            },
        )

        categories_sheet = workbook.create_sheet("Categories")
        categories_sheet.append(CATEGORY_IMAGE_EXCEL_HEADERS)
        self.append_dict_row(
            categories_sheet,
            CATEGORY_IMAGE_EXCEL_HEADERS,
            {
                "category": "shoes",
                "name": "Footwear",
                "slug": "shoes",
                "image": image_value,
                "external_image_url": external_url,
            },
        )

        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        return output

    def test_local_image_path_populates_main_image_fields(self):
        with TemporaryDirectory() as temporary_directory:
            media_root = Path(temporary_directory) / "media"
            image_path = Path(temporary_directory) / "sample.png"
            image_path.write_bytes(self.png_bytes())
            workbook = self.build_workbook(str(image_path))

            with override_settings(MEDIA_ROOT=media_root):
                valid_rows, errors = validate_product_excel_workbook(workbook)
                self.assertEqual(errors, [])
                import_product_excel_rows(valid_rows)

                product = Product.objects.get(sku="SHOES-001")
                company = Company.objects.get(code="Com-1")
                self.category.refresh_from_db()

                self.assertTrue(product.primary_image.name.startswith("products/"))
                self.assertEqual(product.external_image_url, "")
                self.assertTrue(company.logo.name.startswith("product-companies/"))
                self.assertEqual(company.external_logo_url, "")
                self.assertTrue(self.category.cover_image.name.startswith("categories/"))
                self.assertEqual(self.category.external_image_url, "")
                self.assertTrue((media_root / product.primary_image.name).is_file())
                self.assertTrue((media_root / company.logo.name).is_file())
                self.assertTrue((media_root / self.category.cover_image.name).is_file())

    def test_explicit_external_columns_remain_external_fallbacks(self):
        external_url = "https://example.com/external.png"
        workbook = self.build_workbook("", external_url=external_url)

        valid_rows, errors = validate_product_excel_workbook(workbook)
        self.assertEqual(errors, [])
        import_product_excel_rows(valid_rows)

        product = Product.objects.get(sku="SHOES-001")
        company = Company.objects.get(code="Com-1")
        self.category.refresh_from_db()

        self.assertFalse(product.primary_image)
        self.assertEqual(product.external_image_url, external_url)
        self.assertFalse(company.logo)
        self.assertEqual(company.external_logo_url, external_url)
        self.assertFalse(self.category.cover_image)
        self.assertEqual(self.category.external_image_url, external_url)

    def test_url_image_is_downloaded_and_validated(self):
        content = self.png_bytes()

        class FakeResponse(BytesIO):
            headers = {"Content-Length": str(len(content))}

            def geturl(self):
                return "https://example.com/images/logo.png"

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                self.close()

        with patch("apps.dashboard.views.urlopen", return_value=FakeResponse(content)):
            image_data = load_excel_image("https://example.com/logo.png", [])

        self.assertEqual(image_data["name"], "logo.png")
        self.assertEqual(image_data["content"], content)
