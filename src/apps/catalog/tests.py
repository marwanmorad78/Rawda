from decimal import Decimal

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from apps.catalog.cart import (
    add_product,
    add_product_company_option,
    add_product_option,
    build_cart,
    validate_quantity,
)
from apps.catalog.models import (
    Category,
    Product,
    ProductCompany,
    ProductCompanyOption,
    ProductOption,
)


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
        company = ProductCompany.objects.create(product=product, name="Farm")
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
