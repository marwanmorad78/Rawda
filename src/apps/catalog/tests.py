from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from apps.catalog.cart import (
    CART_SESSION_KEY,
    add_product,
    add_product_company_option,
    add_product_option,
    build_cart,
    validate_quantity,
)
from apps.catalog.models import (
    Category,
    Company,
    Product,
    ProductCompany,
    ProductCompanyOption,
    ProductOption,
)
from apps.core.localization import get_ui_strings
from apps.core.models import CustomerOrder


class KiloCartTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.category = Category.objects.create(
            name="Weighted",
            sold_by_weight=True,
            is_price_linked_to_dollar=False,
        )

    def request_with_session(self):
        request = self.factory.get("/")
        SessionMiddleware(lambda current_request: None).process_request(request)
        request.session.save()
        return request

    def weighted_product(self, **overrides):
        defaults = {
            "category": self.category,
            "name": "Tomatoes",
            "price": Decimal("100"),
            "sold_by_weight_mode": Product.BEHAVIOR_CUSTOM,
            "sold_by_weight": True,
        }
        defaults.update(overrides)
        return Product.objects.create(**defaults)

    def test_half_kilo_uses_required_estimated_range(self):
        product = self.weighted_product()
        request = self.request_with_session()

        add_product(request, product.pk, Decimal("0.5"), is_weight_based=True)
        item = build_cart(request)["items"][0]

        self.assertEqual(item["quantity"], Decimal("0.5"))
        self.assertEqual(item["line_total_min"], Decimal("50"))
        self.assertEqual(item["line_total_max"], Decimal("60"))
        self.assertEqual(item["display_quantity"], "500 \u063a")

    def test_weight_validation_enforces_range_and_step(self):
        for valid_quantity in ("0.5", "1", "1.5", "10"):
            self.assertEqual(
                validate_quantity(valid_quantity, is_weight_based=True),
                Decimal(valid_quantity),
            )

        for invalid_quantity in ("0", "0.6", "10.5", "1.25"):
            with self.assertRaises(ValueError):
                validate_quantity(invalid_quantity, is_weight_based=True)

    def test_weighted_option_price_is_per_kilo(self):
        product = self.weighted_product(has_options=True)
        option = ProductOption.objects.create(
            product=product,
            name="Premium",
            price=Decimal("200"),
        )
        request = self.request_with_session()

        add_product_option(request, option.pk, Decimal("1.5"), is_weight_based=True)
        item = build_cart(request)["items"][0]

        self.assertEqual(item["line_total_min"], Decimal("300"))
        self.assertEqual(item["line_total_max"], Decimal("320"))
        self.assertEqual(item["display_quantity"], "1.5 \u0643\u063a")

    def test_weighted_company_option_price_is_per_kilo(self):
        product = self.weighted_product(
            product_type=Product.PRODUCT_TYPE_COMPANY_GROUPED,
        )
        global_company = Company.objects.create(code="farm", name="Farm")
        company = ProductCompany.objects.create(product=product, company=global_company)
        option = ProductCompanyOption.objects.create(
            company=company,
            name="Large",
            price=Decimal("150"),
        )
        request = self.request_with_session()

        add_product_company_option(
            request,
            option.pk,
            Decimal("1"),
            is_weight_based=True,
        )
        item = build_cart(request)["items"][0]

        self.assertEqual(item["line_total_min"], Decimal("150"))
        self.assertEqual(item["line_total_max"], Decimal("165"))
        self.assertEqual(item["display_quantity"], "1 \u0643\u063a")

    def test_accumulated_weight_cannot_exceed_ten_kilos(self):
        product = self.weighted_product()
        request = self.request_with_session()
        add_product(request, product.pk, Decimal("10"), is_weight_based=True)

        with self.assertRaises(ValueError):
            add_product(request, product.pk, Decimal("0.5"), is_weight_based=True)


class CartRemovalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="0999999999",
            password="test-password",
        )
        self.client.force_login(self.user)
        self.category = Category.objects.create(name="Regular")
        self.products = [
            Product.objects.create(
                category=self.category,
                name=f"Product {index}",
                price=Decimal("100"),
                sold_by_weight_mode=Product.BEHAVIOR_CUSTOM,
                sold_by_weight=False,
            )
            for index in range(1, 4)
        ]
        session = self.client.session
        session[CART_SESSION_KEY] = {
            f"product:{product.pk}": {"quantity": "1", "note": ""}
            for product in self.products
        }
        session.save()

    def test_ajax_remove_keeps_remaining_items_after_cart_reload(self):
        removed_product = self.products[0]
        response = self.client.post(
            reverse(
                "catalog:cart-remove",
                kwargs={"item_type": "product", "item_id": removed_product.pk},
            ),
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_empty"])
        self.assertEqual(response.json()["cart_count"], 2)

        reload_response = self.client.get(
            reverse("catalog:cart"),
            HTTP_ACCEPT="text/html",
            HTTP_CACHE_CONTROL="max-age=0",
            HTTP_SEC_FETCH_DEST="document",
        )

        self.assertEqual(reload_response.status_code, 200)
        self.assertEqual(len(reload_response.context["cart"]["items"]), 2)

    def test_ajax_quantity_zero_keeps_other_items_after_cart_reload(self):
        removed_product = self.products[0]
        response = self.client.post(
            reverse(
                "catalog:cart-update",
                kwargs={"item_type": "product", "item_id": removed_product.pk},
            ),
            {"quantity": "0"},
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_empty"])
        self.assertEqual(response.json()["cart_count"], 2)

        reload_response = self.client.get(
            reverse("catalog:cart"),
            HTTP_ACCEPT="text/html",
            HTTP_CACHE_CONTROL="max-age=0",
            HTTP_SEC_FETCH_DEST="document",
        )

        self.assertEqual(len(reload_response.context["cart"]["items"]), 2)


class CheckoutHistoryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="checkout-history",
            password="test-password",
        )
        self.client.force_login(self.user)
        category = Category.objects.create(name="Checkout")
        self.product = Product.objects.create(
            category=category,
            name="Checkout Product",
            price=Decimal("100"),
            sold_by_weight_mode=Product.BEHAVIOR_CUSTOM,
            sold_by_weight=False,
        )
        session = self.client.session
        session[CART_SESSION_KEY] = {
            f"product:{self.product.pk}": {"quantity": "1", "note": ""}
        }
        session.save()

    def test_checkout_replaces_history_with_home_and_disables_caching(self):
        response = self.client.get(reverse("catalog:checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'data-checkout-return-url="{reverse("core:home")}"',
        )
        self.assertIn("no-store", response.headers["Cache-Control"])

    def test_successful_checkout_clears_cart_and_redirects_to_tracking_cart(self):
        response = self.client.post(
            reverse("catalog:checkout-confirm"),
            {"service_type": CustomerOrder.SERVICE_PICKUP},
        )

        self.assertRedirects(response, reverse("catalog:cart"))
        self.assertEqual(CustomerOrder.objects.filter(profile__user=self.user).count(), 1)
        self.assertEqual(self.client.session.get(CART_SESSION_KEY, {}), {})


class CategoriesPageTests(TestCase):
    def setUp(self):
        self.main_category = Category.objects.create(
            name="Fresh Food",
            name_ar="\u0627\u0644\u0623\u063a\u0630\u064a\u0629 \u0627\u0644\u0637\u0627\u0632\u062c\u0629",
            display_order=1,
        )
        self.subcategory = Category.objects.create(
            parent=self.main_category,
            name="Fruit",
            name_ar="\u0627\u0644\u0641\u0648\u0627\u0643\u0647",
            display_order=1,
        )
        Category.objects.create(
            name="Hidden",
            is_active=False,
            display_order=2,
        )
        Category.objects.create(
            parent=self.main_category,
            name="Hidden child",
            is_active=False,
            display_order=2,
        )

    def test_categories_page_lists_active_main_categories_and_subcategories(self):
        response = self.client.get(reverse("catalog:categories"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/categories/")
        self.assertContains(response, self.main_category.name_ar)
        self.assertContains(
            response,
            f"{self.main_category.name_ar} - {self.subcategory.name_ar}",
        )
        self.assertNotContains(response, "Hidden")
        self.assertContains(response, self.main_category.get_absolute_url())
        self.assertContains(response, self.subcategory.get_absolute_url())
        self.assertEqual(len(response.context["category_cards"]), 2)
        self.assertContains(response, 'class="categories-page-card"', count=2)
        self.assertNotContains(response, "categories-page-subcategory")

    def test_categories_nav_link_is_active(self):
        response = self.client.get(reverse("catalog:categories"))

        self.assertContains(
            response,
            f'href="{reverse("catalog:categories")}" class="tab-link is-active"',
            html=False,
        )

    def test_parent_category_uses_category_browsing_labels(self):
        labels = get_ui_strings("ar")

        home_response = self.client.get(reverse("core:home"))
        detail_response = self.client.get(self.main_category.get_absolute_url())

        self.assertContains(home_response, labels["more_categories"])
        self.assertContains(detail_response, labels["browse_categories"])
        self.assertNotContains(detail_response, labels["category_browse"])
