from decimal import Decimal, InvalidOperation
from datetime import datetime, time
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.db.models import ProtectedError, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView
from openpyxl import Workbook, load_workbook

from apps.catalog.models import Category, Product, ProductOption
from apps.core.localization import DEFAULT_LANGUAGE, format_syp, localize_instance, localize_queryset
from apps.core.models import (
    CenterStatus,
    CustomerOrder,
    CustomerOrderItem,
    CustomerProfile,
    DeliveryArea,
    DeliverySubArea,
    SiteSettings,
)
from apps.core.pricing import (
    get_active_site_settings,
    set_product_display_price,
    set_promotion_display_price,
)
from apps.dashboard.forms import (
    CategoryForm,
    CenterStatusForm,
    CustomerAccessPasswordForm,
    CustomerPasswordChangeForm,
    DeliveryAreaExcelUploadForm,
    DeliveryAreaForm,
    DeliverySubAreaFormSet,
    DollarPriceForm,
    ManagerLoginForm,
    OrderAcceptForm,
    ProductExcelUploadForm,
    ProductOptionFormSet,
    ProductForm,
    PromotionForm,
    SiteSettingsForm,
)
from apps.dashboard.localization import get_dashboard_strings
from apps.dashboard.mixins import DashboardLocalizationMixin, StaffRequiredMixin
from apps.core.order_status import attach_order_display, attach_orders_display, suggested_expected_minutes
from apps.core.services import mark_order_accepted, sync_center_status_and_auto_accept_waiting_orders
from apps.promotions.models import Promotion


PRODUCT_EXCEL_HEADERS = [
    "product_name",
    "category",
    "short_description",
    "description",
    "price",
    "price_link_mode",
    "is_price_linked_to_dollar",
    "sold_by_weight_mode",
    "sold_by_weight",
    "has_options",
    "unit_label",
    "is_available",
    "is_featured",
    "external_image_url",
    "sku",
]
PRODUCT_EXCEL_REQUIRED_HEADERS = ["product_name", "category", "price"]
PRODUCT_OPTION_EXCEL_HEADERS = [
    "product_sku",
    "option_name",
    "price",
    "is_default",
    "display_order",
]
PRODUCT_OPTION_EXCEL_REQUIRED_HEADERS = ["product_sku", "option_name", "price"]
BOOLEAN_COLUMNS = ["is_price_linked_to_dollar", "sold_by_weight", "has_options", "is_available", "is_featured"]
PRODUCT_MODE_COLUMNS = {
    "price_link_mode": {Product.BEHAVIOR_INHERIT, Product.BEHAVIOR_CUSTOM},
    "sold_by_weight_mode": {Product.BEHAVIOR_INHERIT, Product.BEHAVIOR_CUSTOM},
}
DELIVERY_AREA_EXCEL_HEADERS = ["area_name", "has_sub_areas", "delivery_fee", "display_order", "is_active"]
DELIVERY_AREA_EXCEL_REQUIRED_HEADERS = ["area_name"]
DELIVERY_SUB_AREA_EXCEL_HEADERS = ["area_name", "sub_area_name", "delivery_fee", "display_order", "is_active"]
DELIVERY_SUB_AREA_EXCEL_REQUIRED_HEADERS = ["area_name", "sub_area_name", "delivery_fee"]
SALES_REPORT_STATUSES = [
    CustomerOrder.STATUS_ACCEPTED,
    CustomerOrder.STATUS_BEING_PREPARED,
    CustomerOrder.STATUS_OUT_FOR_DELIVERY,
    CustomerOrder.STATUS_READY_TO_PICKUP,
    CustomerOrder.STATUS_DONE,
]


def get_dashboard_site_settings():
    site_settings, _ = SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            "store_name": "Al Rawda Center",
            "store_name_ar": "مركز الروضة",
            "about_text": "Update your store information here.",
            "about_text_ar": "حدث معلومات المتجر من هنا.",
            "address": "Damascus",
            "address_ar": "دمشق",
            "primary_phone": "+963-000-000-000",
            "hero_title": "Fresh products for every home",
            "hero_title_ar": "منتجات طازجة لكل بيت",
        },
    )
    return site_settings


def normalize_excel_header(value):
    return str(value or "").strip().lower()


def normalize_excel_text(value):
    if value is None:
        return ""
    return str(value).strip()


def parse_excel_boolean(value, default=False):
    if value is None or value == "":
        return default, None
    if isinstance(value, bool):
        return value, None
    normalized = str(value).strip().lower()
    if normalized in {"true", "yes", "y", "1", "available"}:
        return True, None
    if normalized in {"false", "no", "n", "0", "unavailable"}:
        return False, None
    return default, "Use true or false."


def parse_excel_decimal(value):
    if value is None or value == "":
        return None, "This field is required."
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None, "Enter a valid number."
    if parsed < 0:
        return None, "Price cannot be negative."
    if parsed != parsed.to_integral_value():
        return None, "Enter a whole number without decimals."
    return parsed, None


def parse_excel_integer(value, default=0):
    if value is None or value == "":
        return default, None
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        return default, "Enter a whole number."
    if parsed < 0:
        return default, "Enter zero or a positive number."
    return parsed, None


def build_sheet_rows(worksheet):
    rows = worksheet.iter_rows(values_only=True)
    headers = [normalize_excel_header(value) for value in next(rows, [])]
    header_positions = {header: index for index, header in enumerate(headers) if header}
    data_rows = []
    for row_number, row_values in enumerate(rows, start=2):
        row = {
            header: row_values[index] if index < len(row_values) else None
            for header, index in header_positions.items()
        }
        if any(value not in (None, "") for value in row.values()):
            data_rows.append((row_number, row))
    return header_positions, data_rows


def get_product_excel_category_lookup():
    lookup = {}
    duplicate_names = set()
    for category in Category.objects.all():
        slug_key = (category.slug or "").strip().lower()
        name_key = (category.name or "").strip().lower()
        if slug_key:
            lookup[slug_key] = category
        if name_key:
            if name_key in lookup:
                duplicate_names.add(name_key)
            else:
                lookup[name_key] = category
    return lookup, duplicate_names


def get_product_manage_context(language, product_form=None, upload_form=None, excel_errors=None):
    return {
        "dashboard_ui": get_dashboard_strings(language),
        "form": product_form or ProductForm(language=language),
        "upload_form": upload_form or ProductExcelUploadForm(language=language),
        "excel_errors": excel_errors or [],
    }


def get_product_list_context(language, upload_form=None, excel_errors=None, search_query=""):
    site_settings = get_active_site_settings() or get_dashboard_site_settings()
    items_queryset = Product.objects.select_related("category").all().order_by("name")
    if search_query:
        items_queryset = items_queryset.filter(
            Q(name__icontains=search_query)
            | Q(name_ar__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(category__name_ar__icontains=search_query)
            | Q(sku__icontains=search_query)
        )
    items = list(items_queryset)
    for item in items:
        localize_instance(item.category, language, ["name", "description"])
        localize_instance(item, language, ["name", "short_description", "description", "unit_label"])
        set_product_display_price(item, language, site_settings)
    return {
        "dashboard_ui": get_dashboard_strings(language),
        "items": items,
        "upload_form": upload_form or ProductExcelUploadForm(language=language),
        "excel_errors": excel_errors or [],
        "search_query": search_query,
    }


def get_delivery_area_manage_context(language, area_form=None, upload_form=None, excel_errors=None):
    return {
        "dashboard_ui": get_dashboard_strings(language),
        "form": area_form or DeliveryAreaForm(language=language),
        "upload_form": upload_form or DeliveryAreaExcelUploadForm(language=language),
        "excel_errors": excel_errors or [],
        "items": DeliveryArea.objects.prefetch_related("sub_areas").all(),
    }


def validate_product_excel_workbook(excel_file, language=DEFAULT_LANGUAGE):
    dashboard_ui = get_dashboard_strings(language)
    # Validate the entire workbook before importing so partial product batches are avoided.
    try:
        workbook = load_workbook(excel_file, read_only=True, data_only=True)
    except Exception:
        return [], [dashboard_ui["excel_read_error"]]

    products_sheet = workbook["Products"] if "Products" in workbook.sheetnames else workbook.active
    header_positions, product_sheet_rows = build_sheet_rows(products_sheet)
    option_header_positions = {}
    option_sheet_rows = []
    option_product_skus = set()
    if "Options" in workbook.sheetnames:
        option_header_positions, option_sheet_rows = build_sheet_rows(workbook["Options"])
        if "product_sku" in option_header_positions:
            option_product_skus = {
                normalize_excel_text(row.get("product_sku")).lower()
                for _, row in option_sheet_rows
                if normalize_excel_text(row.get("product_sku"))
            }
    missing_headers = [
        header for header in PRODUCT_EXCEL_REQUIRED_HEADERS if header not in header_positions
    ]
    if missing_headers:
        return [], [f"Missing required column: {', '.join(missing_headers)}"]

    category_lookup, duplicate_names = get_product_excel_category_lookup()
    valid_rows = []
    valid_options = []
    errors = []
    seen_import_keys = set()

    for row_number, row in product_sheet_rows:
        row_errors = []
        product_name = normalize_excel_text(row.get("product_name"))
        category_value = normalize_excel_text(row.get("category"))
        sku = normalize_excel_text(row.get("sku"))

        if not product_name:
            row_errors.append("product_name is required.")

        category = None
        category_key = category_value.lower()
        if not category_value:
            row_errors.append("category is required.")
        elif category_key in duplicate_names:
            row_errors.append("category name is duplicated; use the category slug instead.")
        else:
            category = category_lookup.get(category_key)
            if not category:
                row_errors.append(f"category '{category_value}' does not exist.")

        parsed_booleans = {}
        for column in BOOLEAN_COLUMNS:
            default = column == "is_available"
            parsed_booleans[column], boolean_error = parse_excel_boolean(row.get(column), default)
            if boolean_error:
                row_errors.append(f"{column}: {boolean_error}")

        has_options = parsed_booleans["has_options"] or bool(sku and sku.lower() in option_product_skus)
        price, price_error = parse_excel_decimal(row.get("price"))
        if price_error and has_options and row.get("price") in (None, ""):
            price = Decimal("0")
        elif price_error:
            row_errors.append(f"price: {price_error}")

        parsed_modes = {}
        for column, choices in PRODUCT_MODE_COLUMNS.items():
            value = normalize_excel_text(row.get(column)) or Product.BEHAVIOR_INHERIT
            if value not in choices:
                row_errors.append(f"{column}: use inherit or custom.")
            parsed_modes[column] = value

        import_key = ("sku", sku.lower()) if sku else ("name", getattr(category, "id", None), product_name.lower())
        if import_key in seen_import_keys:
            row_errors.append("This product appears more than once in this file.")
        seen_import_keys.add(import_key)

        if sku and category is not None and product_name:
            product_by_sku = Product.objects.filter(sku__iexact=sku).first()
            product_by_name = Product.objects.filter(category=category, name__iexact=product_name).first()
            if product_by_sku and product_by_name and product_by_sku.pk != product_by_name.pk:
                row_errors.append(
                    f"sku '{sku}' belongs to a different product than '{product_name}'."
                )

        if row_errors:
            errors.append(f"Row {row_number}: {' '.join(row_errors)}")
            continue

        row_data = {
            "category": category,
            "name": product_name,
            "short_description": normalize_excel_text(row.get("short_description")),
            "description": normalize_excel_text(row.get("description")),
            "price": price,
            "price_link_mode": parsed_modes["price_link_mode"],
            "is_price_linked_to_dollar": parsed_booleans["is_price_linked_to_dollar"],
            "sold_by_weight_mode": parsed_modes["sold_by_weight_mode"],
            "sold_by_weight": parsed_booleans["sold_by_weight"],
            "has_options": has_options,
            "unit_label": normalize_excel_text(row.get("unit_label")) or "per item",
            "is_available": parsed_booleans["is_available"],
            "is_featured": parsed_booleans["is_featured"],
            "external_image_url": normalize_excel_text(row.get("external_image_url")),
            "sku": sku,
        }
        row_data["_import_keys"] = [import_key]
        if sku:
            row_data["_import_keys"].append(("name", getattr(category, "id", None), product_name.lower()))
        valid_rows.append(row_data)

    if "Options" in workbook.sheetnames:
        if option_sheet_rows:
            missing_option_headers = [
                header for header in PRODUCT_OPTION_EXCEL_REQUIRED_HEADERS if header not in option_header_positions
            ]
            if missing_option_headers:
                errors.append(f"Options sheet missing required column: {', '.join(missing_option_headers)}")

        seen_option_keys = set()
        known_product_keys = {
            import_key
            for valid_row in valid_rows
            for import_key in valid_row.get("_import_keys", [])
        }
        for row_number, row in option_sheet_rows:
            row_errors = []
            product_sku = normalize_excel_text(row.get("product_sku"))
            option_name = normalize_excel_text(row.get("option_name"))

            if not product_sku:
                row_errors.append("product_sku is required.")
            if not option_name:
                row_errors.append("option_name is required.")

            price, price_error = parse_excel_decimal(row.get("price"))
            if price_error:
                row_errors.append(f"price: {price_error}")

            is_default, boolean_error = parse_excel_boolean(row.get("is_default"), False)
            if boolean_error:
                row_errors.append(f"is_default: {boolean_error}")

            display_order, display_order_error = parse_excel_integer(row.get("display_order"), 0)
            if display_order_error:
                row_errors.append(f"display_order: {display_order_error}")

            product_key = ("sku", product_sku.lower()) if product_sku else None
            if product_key and product_key not in known_product_keys and not Product.objects.filter(sku__iexact=product_sku).exists():
                row_errors.append(f"product_sku '{product_sku}' does not match an imported or existing product.")

            option_key = (product_key, option_name.lower())
            if product_key and option_name:
                if option_key in seen_option_keys:
                    row_errors.append("This option appears more than once for the same product in this file.")
                seen_option_keys.add(option_key)

            if row_errors:
                errors.append(f"Options row {row_number}: {' '.join(row_errors)}")
                continue

            valid_options.append(
                {
                    "product_key": product_key,
                    "name": option_name,
                    "price": price,
                    "is_default": is_default,
                    "display_order": display_order,
                }
            )

    if not valid_rows and not errors:
        errors.append("The uploaded workbook has no product rows.")

    return {"products": valid_rows, "options": valid_options}, errors


def find_existing_product_for_import(row):
    sku = (row.get("sku") or "").strip()
    if sku:
        existing_product = Product.objects.filter(sku__iexact=sku).first()
        if existing_product is not None:
            return existing_product
    return Product.objects.filter(category=row["category"], name__iexact=row["name"]).first()


def merge_duplicate_products_for_import():
    duplicates_removed = 0
    seen_keys = set()

    for product in Product.objects.select_related("category").order_by("id"):
        keys = []
        if product.sku:
            keys.append(("sku", product.sku.strip().lower()))
        keys.append(("name", product.category_id, product.name.strip().lower()))

        if any(key in seen_keys for key in keys):
            product.delete()
            duplicates_removed += 1
            continue

        seen_keys.update(keys)

    return duplicates_removed


def resolve_imported_product(product_lookup, product_key):
    product = product_lookup.get(product_key)
    if product is not None:
        return product
    if product_key and product_key[0] == "sku":
        return Product.objects.filter(sku__iexact=product_key[1]).first()
    if product_key and product_key[0] == "name":
        return Product.objects.filter(category_id=product_key[1], name__iexact=product_key[2]).first()
    return None


def import_product_excel_rows(valid_rows):
    # Existing products are matched by SKU when present, otherwise by category and product name.
    product_rows = valid_rows["products"] if isinstance(valid_rows, dict) else valid_rows
    option_rows = valid_rows.get("options", []) if isinstance(valid_rows, dict) else []
    created = 0
    updated = 0
    now = timezone.now()

    with transaction.atomic():
        merge_duplicate_products_for_import()
        product_lookup = {}
        for row in product_rows:
            import_keys = row.pop("_import_keys", [])
            existing_product = find_existing_product_for_import(row)
            if existing_product:
                update_data = row.copy()
                if not update_data["sku"]:
                    update_data.pop("sku")
                update_data["updated_at"] = now
                Product.objects.filter(pk=existing_product.pk).update(**update_data)
                product = Product.objects.get(pk=existing_product.pk)
                updated += 1
            else:
                product = Product(**row)
                product.save()
                created += 1
            for import_key in import_keys:
                product_lookup[import_key] = product

        option_products = set()
        for row in option_rows:
            product = resolve_imported_product(product_lookup, row["product_key"])
            if product is None:
                continue
            option_products.add(product.pk)
            option_data = {
                "price": row["price"],
                "is_default": row["is_default"],
                "display_order": row["display_order"],
            }
            if row["is_default"]:
                product.options.update(is_default=False)
            option = product.options.filter(name__iexact=row["name"]).first()
            if option:
                ProductOption.objects.filter(pk=option.pk).update(name=row["name"], **option_data)
            else:
                ProductOption.objects.create(product=product, name=row["name"], **option_data)

        if option_products:
            Product.objects.filter(pk__in=option_products).update(has_options=True, updated_at=now)

    return created, updated


def validate_delivery_area_excel_workbook(excel_file, language=DEFAULT_LANGUAGE):
    dashboard_ui = get_dashboard_strings(language)
    try:
        workbook = load_workbook(excel_file, read_only=True, data_only=True)
    except Exception:
        return {}, [dashboard_ui["excel_read_error"]]

    areas_sheet = workbook["Areas"] if "Areas" in workbook.sheetnames else workbook.active
    area_header_positions, area_sheet_rows = build_sheet_rows(areas_sheet)
    missing_headers = [
        header for header in DELIVERY_AREA_EXCEL_REQUIRED_HEADERS if header not in area_header_positions
    ]
    if missing_headers:
        return {}, [f"Areas sheet missing required column: {', '.join(missing_headers)}"]

    valid_areas = []
    valid_sub_areas = []
    errors = []
    seen_area_names = set()
    known_area_names = {area.name.strip().lower() for area in DeliveryArea.objects.all()}
    sub_header_positions = {}
    sub_sheet_rows = []
    sub_area_area_names = set()
    if "SubAreas" in workbook.sheetnames:
        sub_header_positions, sub_sheet_rows = build_sheet_rows(workbook["SubAreas"])
        sub_area_area_names = {
            normalize_excel_text(row.get("area_name")).lower()
            for _, row in sub_sheet_rows
            if normalize_excel_text(row.get("area_name"))
        }

    for row_number, row in area_sheet_rows:
        row_errors = []
        area_name = normalize_excel_text(row.get("area_name"))
        if not area_name:
            row_errors.append("area_name is required.")
        area_key = area_name.lower()
        if area_key in seen_area_names:
            row_errors.append("This area appears more than once in this file.")
        if area_key:
            seen_area_names.add(area_key)
            known_area_names.add(area_key)

        has_sub_areas, boolean_error = parse_excel_boolean(row.get("has_sub_areas"), False)
        if boolean_error:
            row_errors.append(f"has_sub_areas: {boolean_error}")
        has_sub_areas = has_sub_areas or bool(area_key and area_key in sub_area_area_names)

        delivery_fee, fee_error = parse_excel_decimal(row.get("delivery_fee"))
        if fee_error and has_sub_areas and row.get("delivery_fee") in (None, ""):
            delivery_fee = Decimal("0")
        elif fee_error:
            row_errors.append(f"delivery_fee: {fee_error}")

        display_order, order_error = parse_excel_integer(row.get("display_order"), 0)
        if order_error:
            row_errors.append(f"display_order: {order_error}")

        is_active, active_error = parse_excel_boolean(row.get("is_active"), True)
        if active_error:
            row_errors.append(f"is_active: {active_error}")

        if row_errors:
            errors.append(f"Areas row {row_number}: {' '.join(row_errors)}")
            continue

        valid_areas.append(
            {
                "name": area_name,
                "has_sub_areas": has_sub_areas,
                "delivery_fee": delivery_fee,
                "display_order": display_order,
                "is_active": is_active,
            }
        )

    if "SubAreas" in workbook.sheetnames:
        if sub_sheet_rows:
            missing_sub_headers = [
                header for header in DELIVERY_SUB_AREA_EXCEL_REQUIRED_HEADERS if header not in sub_header_positions
            ]
            if missing_sub_headers:
                errors.append(f"SubAreas sheet missing required column: {', '.join(missing_sub_headers)}")

        seen_sub_area_keys = set()
        for row_number, row in sub_sheet_rows:
            row_errors = []
            area_name = normalize_excel_text(row.get("area_name"))
            sub_area_name = normalize_excel_text(row.get("sub_area_name"))
            area_key = area_name.lower()

            if not area_name:
                row_errors.append("area_name is required.")
            elif area_key not in known_area_names:
                row_errors.append(f"area_name '{area_name}' does not match an imported or existing area.")
            if not sub_area_name:
                row_errors.append("sub_area_name is required.")

            delivery_fee, fee_error = parse_excel_decimal(row.get("delivery_fee"))
            if fee_error:
                row_errors.append(f"delivery_fee: {fee_error}")

            display_order, order_error = parse_excel_integer(row.get("display_order"), 0)
            if order_error:
                row_errors.append(f"display_order: {order_error}")

            is_active, active_error = parse_excel_boolean(row.get("is_active"), True)
            if active_error:
                row_errors.append(f"is_active: {active_error}")

            sub_key = (area_key, sub_area_name.lower())
            if area_key and sub_area_name:
                if sub_key in seen_sub_area_keys:
                    row_errors.append("This sub-area appears more than once for the same area in this file.")
                seen_sub_area_keys.add(sub_key)

            if row_errors:
                errors.append(f"SubAreas row {row_number}: {' '.join(row_errors)}")
                continue

            valid_sub_areas.append(
                {
                    "area_name": area_name,
                    "name": sub_area_name,
                    "delivery_fee": delivery_fee,
                    "display_order": display_order,
                    "is_active": is_active,
                }
            )

    if not valid_areas and not errors:
        errors.append("The uploaded workbook has no delivery area rows.")

    return {"areas": valid_areas, "sub_areas": valid_sub_areas}, errors


def import_delivery_area_excel_rows(valid_rows):
    area_rows = valid_rows.get("areas", [])
    sub_area_rows = valid_rows.get("sub_areas", [])
    created = 0
    updated = 0
    area_lookup = {}
    sub_area_area_names = {row["area_name"].strip().lower() for row in sub_area_rows}

    with transaction.atomic():
        for row in area_rows:
            area_key = row["name"].strip().lower()
            row_data = row.copy()
            if area_key in sub_area_area_names:
                row_data["has_sub_areas"] = True
                row_data["delivery_fee"] = Decimal("0")
            area = DeliveryArea.objects.filter(name__iexact=row["name"]).first()
            if area:
                for field, value in row_data.items():
                    setattr(area, field, value)
                area.save()
                updated += 1
            else:
                area = DeliveryArea.objects.create(**row_data)
                created += 1
            area_lookup[area_key] = area

        for row in sub_area_rows:
            area_key = row["area_name"].strip().lower()
            area = area_lookup.get(area_key) or DeliveryArea.objects.filter(name__iexact=row["area_name"]).first()
            if area is None:
                continue
            area.has_sub_areas = True
            area.delivery_fee = Decimal("0")
            area.save(update_fields=["has_sub_areas", "delivery_fee", "updated_at"])
            sub_area = area.sub_areas.filter(name__iexact=row["name"]).first()
            sub_data = {
                "delivery_fee": row["delivery_fee"],
                "display_order": row["display_order"],
                "is_active": row["is_active"],
            }
            if sub_area:
                DeliverySubArea.objects.filter(pk=sub_area.pk).update(name=row["name"], **sub_data)
            else:
                DeliverySubArea.objects.create(area=area, name=row["name"], **sub_data)

    return created, updated


def product_options_have_rows(option_formset):
    return any(
        form.cleaned_data
        and not form.cleaned_data.get("DELETE")
        and form.cleaned_data.get("name")
        and form.cleaned_data.get("price") is not None
        for form in option_formset.forms
    )


def save_product_options(product, option_formset):
    if not product.has_options:
        product.options.all().delete()
        return
    option_formset.instance = product
    option_formset.save()


class ManagerLoginView(DashboardLocalizationMixin, LoginView):
    template_name = "dashboard/login.html"
    authentication_form = ManagerLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_staff:
            form.add_error(None, self.get_dashboard_ui()["staff_only_error"])
            return self.form_invalid(form)
        return super().form_valid(form)


class ManagerLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


class DashboardHomeView(DashboardLocalizationMixin, StaffRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        sync_center_status_and_auto_accept_waiting_orders(print_invoices=True)
        context = super().get_context_data(**kwargs)
        context["category_count"] = Category.objects.count()
        context["product_count"] = Product.objects.count()
        context["available_product_count"] = Product.objects.filter(is_available=True).count()
        context["promotion_count"] = Promotion.objects.filter(is_active=True).count()
        context["delivery_area_count"] = DeliveryArea.objects.count()
        context["customer_count"] = CustomerProfile.objects.count()
        context["order_count"] = CustomerOrder.objects.count()
        context["pending_order_count"] = CustomerOrder.objects.filter(status__in=CustomerOrder.ACTIVE_STATUSES).count()
        return context


class CenterStatusManageView(DashboardLocalizationMixin, StaffRequiredMixin, TemplateView):
    template_name = "dashboard/center_status.html"

    def get_center_status(self):
        return CenterStatus.get_current().refresh_availability()

    def get_context_data(self, **kwargs):
        sync_center_status_and_auto_accept_waiting_orders(print_invoices=True)
        context = super().get_context_data(**kwargs)
        center_status = self.get_center_status()
        remaining_seconds = max(int(center_status.remaining_busy_time().total_seconds()), 0)
        remaining_minutes = (remaining_seconds + 59) // 60
        context["center_status"] = center_status
        context["remaining_seconds"] = remaining_seconds
        context["remaining_minutes"] = remaining_minutes
        context["form"] = kwargs.get("form") or CenterStatusForm(
            instance=center_status,
            language=self.get_language(),
        )
        return context

    def post(self, request, *args, **kwargs):
        center_status = self.get_center_status()
        form = CenterStatusForm(request.POST, instance=center_status, language=self.get_language())
        if form.is_valid():
            form.save(user=request.user)
            sync_center_status_and_auto_accept_waiting_orders(print_invoices=True)
            messages.success(request, self.get_dashboard_ui()["center_status_updated"])
            return redirect("dashboard:center-status")
        return self.render_to_response(self.get_context_data(form=form))


CUSTOMER_ACCESS_SESSION_KEY = "dashboard_customer_access_granted"


def attach_dashboard_order_display(orders, language):
    return attach_orders_display(
        orders,
        get_dashboard_strings(language),
        language,
        print_auto_accepted_order=True,
    )


def parse_report_date(value):
    if not value:
        return None, None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), None
    except ValueError:
        return None, "Use YYYY-MM-DD."


def get_sales_report_filters(request, dashboard_ui, require_dates=False):
    single_day = (request.GET.get("single_day") or "").strip()
    from_value = (request.GET.get("from_date") or "").strip()
    to_value = (request.GET.get("to_date") or "").strip()
    if single_day:
        from_value = single_day
        to_value = single_day

    errors = []
    from_date, from_error = parse_report_date(from_value)
    to_date, to_error = parse_report_date(to_value)
    if from_error:
        errors.append(f"{dashboard_ui['sales_from_date']}: {from_error}")
    if to_error:
        errors.append(f"{dashboard_ui['sales_to_date']}: {to_error}")
    if require_dates and not from_value:
        errors.append(dashboard_ui["sales_from_date_required"])
    if require_dates and not to_value:
        errors.append(dashboard_ui["sales_to_date_required"])
    if from_date and to_date and from_date > to_date:
        errors.append(dashboard_ui["sales_date_order_error"])

    return {
        "from_date": from_value,
        "to_date": to_value,
        "single_day": single_day,
        "from_date_obj": from_date,
        "to_date_obj": to_date,
        "errors": errors,
    }


def get_sales_report_orders(from_date, to_date):
    start_at = timezone.make_aware(datetime.combine(from_date, time.min))
    end_at = timezone.make_aware(datetime.combine(to_date, time.max))
    return CustomerOrder.objects.filter(
        status__in=SALES_REPORT_STATUSES,
        created_at__gte=start_at,
        created_at__lte=end_at,
    )


def get_order_day_filter(request, dashboard_ui):
    day_value = (request.GET.get("order_day") or "").strip()
    day, day_error = parse_report_date(day_value)
    errors = []
    if day_error:
        errors.append(f"{dashboard_ui['orders_filter_day']}: {day_error}")
    return {"day": day_value, "day_obj": day, "errors": errors}


def filter_orders_by_day(queryset, day):
    if day is None:
        return queryset
    start_at = timezone.make_aware(datetime.combine(day, time.min))
    end_at = timezone.make_aware(datetime.combine(day, time.max))
    return queryset.filter(created_at__gte=start_at, created_at__lte=end_at)


def build_sales_report(from_date, to_date, language):
    orders = get_sales_report_orders(from_date, to_date)
    item_rows = (
        CustomerOrderItem.objects.filter(order__in=orders)
        .values("title", "category_label", "unit_price")
        .annotate(quantity_sold=Sum("quantity"), total_product_price=Sum("line_total_max"))
        .order_by("category_label", "title", "unit_price")
    )
    rows = []
    for row in item_rows:
        unit_price = row["unit_price"] or Decimal("0")
        total_product_price = row["total_product_price"] or Decimal("0")
        rows.append(
            {
                **row,
                "display_unit_price": format_syp(unit_price, language),
                "display_total_product_price": format_syp(total_product_price, language),
            }
        )

    summary = orders.aggregate(grand_total=Sum("total_max"), delivery_total=Sum("delivery_fee"))
    order_count = orders.count()
    grand_total = summary["grand_total"] or Decimal("0")
    delivery_total = summary["delivery_total"] or Decimal("0")
    return {
        "rows": rows,
        "summary": {
            "order_count": order_count,
            "grand_total": grand_total,
            "delivery_total": delivery_total,
            "display_grand_total": format_syp(grand_total, language),
            "display_delivery_total": format_syp(delivery_total, language),
            "from_date": from_date,
            "to_date": to_date,
        },
    }


def decimal_to_excel_number(value):
    return int(value or 0)


class CustomerAccessRequiredMixin:
    def has_customer_access(self):
        return bool(self.request.session.get(CUSTOMER_ACCESS_SESSION_KEY))


class CustomerListView(CustomerAccessRequiredMixin, DashboardLocalizationMixin, StaffRequiredMixin, TemplateView):
    template_name = "dashboard/customers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_customer_access"] = self.has_customer_access()
        context["access_form"] = kwargs.get("access_form") or CustomerAccessPasswordForm(language=self.get_language())
        if context["has_customer_access"]:
            search_query = self.request.GET.get("q", "").strip()
            customers = CustomerProfile.objects.select_related("user").order_by("full_name", "phone_number")
            if search_query:
                customers = customers.filter(
                    Q(full_name__icontains=search_query)
                    | Q(phone_number__icontains=search_query)
                    | Q(user__username__icontains=search_query)
                )
            context["customers"] = customers
            context["search_query"] = search_query
        return context

    def post(self, request, *args, **kwargs):
        form = CustomerAccessPasswordForm(request.POST, language=self.get_language())
        if form.is_valid():
            request.session[CUSTOMER_ACCESS_SESSION_KEY] = True
            request.session.modified = True
            messages.success(request, self.get_dashboard_ui()["customers_unlocked"])
            return redirect("dashboard:customers")
        return self.render_to_response(self.get_context_data(access_form=form))


class CustomerDetailView(CustomerAccessRequiredMixin, DashboardLocalizationMixin, StaffRequiredMixin, TemplateView):
    template_name = "dashboard/customer_detail.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.has_customer_access():
            return redirect("dashboard:customers")
        self.customer = get_object_or_404(
            CustomerProfile.objects.select_related("user").prefetch_related("addresses__area", "addresses__sub_area"),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.get_language()
        orders = list(self.customer.orders.prefetch_related("items").all())
        context["customer"] = self.customer
        context["password_form"] = kwargs.get("password_form") or CustomerPasswordChangeForm(language=language)
        context["orders"] = attach_dashboard_order_display(orders, language)
        return context

    def post(self, request, *args, **kwargs):
        form = CustomerPasswordChangeForm(request.POST, language=self.get_language())
        if form.is_valid():
            self.customer.user.set_password(form.cleaned_data["new_password"])
            self.customer.user.save(update_fields=["password"])
            messages.success(request, self.get_dashboard_ui()["customer_password_updated"])
            return redirect("dashboard:customer-detail", pk=self.customer.pk)
        return self.render_to_response(self.get_context_data(password_form=form))


class DashboardOrdersView(DashboardLocalizationMixin, StaffRequiredMixin, TemplateView):
    template_name = "dashboard/orders.html"

    def get_context_data(self, **kwargs):
        sync_center_status_and_auto_accept_waiting_orders(print_invoices=True)
        context = super().get_context_data(**kwargs)
        dashboard_ui = self.get_dashboard_ui()
        report_filters = get_sales_report_filters(self.request, dashboard_ui)
        order_day_filter = get_order_day_filter(self.request, dashboard_ui)
        report = None
        if report_filters["from_date_obj"] and report_filters["to_date_obj"] and not report_filters["errors"]:
            report = build_sales_report(
                report_filters["from_date_obj"],
                report_filters["to_date_obj"],
                self.get_language(),
            )
        orders_queryset = (
            CustomerOrder.objects.select_related("profile", "address").prefetch_related("items").all()
        )
        if not order_day_filter["errors"]:
            orders_queryset = filter_orders_by_day(orders_queryset, order_day_filter["day_obj"])
        orders = list(orders_queryset)
        context["orders"] = attach_dashboard_order_display(orders, self.get_language())
        context["order_day_filter"] = order_day_filter
        context["order_filter_errors"] = order_day_filter["errors"]
        context["sales_report_filters"] = report_filters
        context["sales_report"] = report
        context["sales_report_errors"] = report_filters["errors"]
        suggested_minutes = suggested_expected_minutes()
        for order in context["orders"]:
            order.suggested_expected_minutes = suggested_minutes
        return context


class SalesReportExcelExportView(DashboardLocalizationMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        dashboard_ui = self.get_dashboard_ui()
        report_filters = get_sales_report_filters(request, dashboard_ui, require_dates=True)
        if report_filters["errors"]:
            for error in report_filters["errors"]:
                messages.error(request, error)
            return redirect("dashboard:orders")

        report = build_sales_report(
            report_filters["from_date_obj"],
            report_filters["to_date_obj"],
            self.get_language(),
        )
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Sales Report"
        worksheet.append([dashboard_ui["sales_report"]])
        worksheet.append(
            [
                dashboard_ui["sales_date_range"],
                f"{report_filters['from_date']} - {report_filters['to_date']}",
            ]
        )
        worksheet.append([])
        worksheet.append(
            [
                dashboard_ui["sales_product_name"],
                dashboard_ui["sales_category"],
                dashboard_ui["sales_quantity_sold"],
                dashboard_ui["sales_unit_price"],
                dashboard_ui["sales_total_product_price"],
            ]
        )
        for row in report["rows"]:
            worksheet.append(
                [
                    row["title"],
                    row["category_label"],
                    row["quantity_sold"] or 0,
                    decimal_to_excel_number(row["unit_price"]),
                    decimal_to_excel_number(row["total_product_price"]),
                ]
            )
        worksheet.append([])
        worksheet.append([dashboard_ui["sales_grand_total"], decimal_to_excel_number(report["summary"]["grand_total"])])
        worksheet.append([dashboard_ui["sales_delivery_total"], decimal_to_excel_number(report["summary"]["delivery_total"])])
        worksheet.append([dashboard_ui["sales_order_count"], report["summary"]["order_count"]])
        worksheet.append(
            [
                dashboard_ui["sales_date_range"],
                f"{report_filters['from_date']} - {report_filters['to_date']}",
            ]
        )
        for column_cells in worksheet.columns:
            header = str(column_cells[0].value or "")
            worksheet.column_dimensions[column_cells[0].column_letter].width = max(len(header) + 6, 18)

        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        filename = f"sales-report-{report_filters['from_date']}-to-{report_filters['to_date']}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class PendingOrdersView(DashboardLocalizationMixin, StaffRequiredMixin, TemplateView):
    template_name = "dashboard/pending_orders.html"

    def get_context_data(self, **kwargs):
        sync_center_status_and_auto_accept_waiting_orders(print_invoices=True)
        context = super().get_context_data(**kwargs)
        orders = list(
            CustomerOrder.objects.select_related("profile", "address")
            .prefetch_related("items")
            .filter(status__in=CustomerOrder.ACTIVE_STATUSES)
            .order_by("created_at", "id")
        )
        context["orders"] = attach_dashboard_order_display(orders, self.get_language())
        return context


class DashboardOrderDetailView(DashboardLocalizationMixin, StaffRequiredMixin, TemplateView):
    template_name = "dashboard/order_detail.html"

    def dispatch(self, request, *args, **kwargs):
        sync_center_status_and_auto_accept_waiting_orders(print_invoices=True)
        self.order = get_object_or_404(
            CustomerOrder.objects.select_related("profile", "address").prefetch_related("items"),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.get_language()
        context["order"] = attach_order_display(
            self.order,
            self.get_dashboard_ui(),
            language,
            print_auto_accepted_order=True,
        )
        context["accept_form"] = kwargs.get("accept_form") or OrderAcceptForm(
            language=language,
            suggested_minutes=suggested_expected_minutes(),
        )
        return context


class DashboardOrderAcceptView(DashboardLocalizationMixin, StaffRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(CustomerOrder, pk=pk, status=CustomerOrder.STATUS_WAITING_ACCEPT)
        form = OrderAcceptForm(
            request.POST,
            language=self.get_language(),
            suggested_minutes=suggested_expected_minutes(),
        )
        if not form.is_valid():
            detail = DashboardOrderDetailView()
            detail.setup(request, pk=pk)
            detail.order = order
            return detail.render_to_response(detail.get_context_data(accept_form=form))

        mark_order_accepted(
            order,
            expected_time_minutes=form.cleaned_data["expected_time_minutes"],
            print_invoice=True,
        )
        messages.success(request, self.get_dashboard_ui()["order_accepted"])
        return redirect("dashboard:pending-order-detail", pk=order.pk)


class DashboardOrderAdvanceView(DashboardLocalizationMixin, StaffRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        sync_center_status_and_auto_accept_waiting_orders(print_invoices=True)
        order = get_object_or_404(CustomerOrder, pk=pk)
        if order.status in {CustomerOrder.STATUS_WAITING_ACCEPT, CustomerOrder.STATUS_WAITING_BUSY_CENTER}:
            messages.error(request, self.get_dashboard_ui()["invalid_order_status_change"])
            return redirect("dashboard:pending-order-detail", pk=order.pk)
        next_status = order.get_next_status()
        requested_status = request.POST.get("status")
        if not next_status or requested_status != next_status:
            messages.error(request, self.get_dashboard_ui()["invalid_order_status_change"])
            return redirect("dashboard:pending-order-detail", pk=order.pk)

        order.status = next_status
        update_fields = ["status", "updated_at"]
        if next_status == CustomerOrder.STATUS_DONE:
            order.completed_at = timezone.now()
            update_fields.append("completed_at")
        order.save(update_fields=update_fields)
        messages.success(request, self.get_dashboard_ui()["order_status_updated"])
        if order.status == CustomerOrder.STATUS_DONE:
            return redirect("dashboard:orders")
        return redirect("dashboard:pending-order-detail", pk=order.pk)


class CategoryManageView(DashboardLocalizationMixin, StaffRequiredMixin, CreateView):
    template_name = "dashboard/manage_categories.html"
    form_class = CategoryForm
    success_url = reverse_lazy("dashboard:categories")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.get_language()
        search_query = self.request.GET.get("q", "").strip()
        items = Category.objects.all().order_by("display_order", "name")
        if search_query:
            items = items.filter(
                Q(name__icontains=search_query)
                | Q(name_ar__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(description_ar__icontains=search_query)
                | Q(slug__icontains=search_query)
            )
        context["items"] = localize_queryset(
            items,
            language,
            ["name", "description"],
        )
        context["search_query"] = search_query
        return context

    def form_valid(self, form):
        messages.success(self.request, self.get_dashboard_ui()["category_saved"])
        return super().form_valid(form)


class CategoryUpdateView(DashboardLocalizationMixin, StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "dashboard/form_page.html"
    success_url = reverse_lazy("dashboard:categories")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_dashboard_ui()["edit_category"]
        return context

    def form_valid(self, form):
        messages.success(self.request, self.get_dashboard_ui()["category_updated"])
        return super().form_valid(form)


class CategoryDeleteView(DashboardLocalizationMixin, StaffRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("dashboard:categories")

    def post(self, request, *args, **kwargs):
        messages.success(request, self.get_dashboard_ui()["category_deleted"])
        return super().post(request, *args, **kwargs)


class ProductManageView(DashboardLocalizationMixin, StaffRequiredMixin, CreateView):
    template_name = "dashboard/manage_products.html"
    form_class = ProductForm
    success_url = reverse_lazy("dashboard:products")

    def get_option_formset(self, data=None):
        return ProductOptionFormSet(data=data, prefix="options")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_product_manage_context(self.get_language(), product_form=context.get("form")))
        context["option_formset"] = kwargs.get("option_formset") or self.get_option_formset()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        option_formset = self.get_option_formset(request.POST)
        if form.is_valid() and option_formset.is_valid():
            if form.cleaned_data.get("has_options") and not product_options_have_rows(option_formset):
                option_formset._non_form_errors = option_formset.error_class(
                    ["Add at least one option when product options are enabled."]
                )
            else:
                return self.save_valid_product(form, option_formset)
        return self.form_invalid(form, option_formset)

    def save_valid_product(self, form, option_formset):
        with transaction.atomic():
            product = form.save()
            save_product_options(product, option_formset)
        messages.success(self.request, self.get_dashboard_ui()["product_saved"])
        return redirect(self.success_url)

    def form_invalid(self, form, option_formset=None):
        context = self.get_context_data(form=form, option_formset=option_formset)
        return self.render_to_response(context)


class ProductListView(DashboardLocalizationMixin, StaffRequiredMixin, TemplateView):
    template_name = "dashboard/product_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get("q", "").strip()
        context.update(get_product_list_context(self.get_language(), search_query=search_query))
        return context


class ProductUpdateView(DashboardLocalizationMixin, StaffRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/form_page.html"
    success_url = reverse_lazy("dashboard:product-list")

    def get_option_formset(self, data=None):
        return ProductOptionFormSet(data=data, instance=self.object, prefix="options")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_dashboard_ui()["edit_product"]
        context["option_formset"] = kwargs.get("option_formset") or self.get_option_formset()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        option_formset = self.get_option_formset(request.POST)
        if form.is_valid() and option_formset.is_valid():
            if form.cleaned_data.get("has_options") and not product_options_have_rows(option_formset):
                option_formset._non_form_errors = option_formset.error_class(
                    ["Add at least one option when product options are enabled."]
                )
            else:
                return self.save_valid_product(form, option_formset)
        return self.form_invalid(form, option_formset)

    def save_valid_product(self, form, option_formset):
        with transaction.atomic():
            product = form.save()
            save_product_options(product, option_formset)
        messages.success(self.request, self.get_dashboard_ui()["product_updated"])
        return redirect(self.success_url)

    def form_invalid(self, form, option_formset=None):
        context = self.get_context_data(form=form, option_formset=option_formset)
        return self.render_to_response(context)


class ProductDeleteView(DashboardLocalizationMixin, StaffRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy("dashboard:product-list")

    def post(self, request, *args, **kwargs):
        messages.success(request, self.get_dashboard_ui()["product_deleted"])
        return super().post(request, *args, **kwargs)


class ProductExcelTemplateView(DashboardLocalizationMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        workbook = Workbook()
        products_sheet = workbook.active
        products_sheet.title = "Products"
        products_sheet.append(PRODUCT_EXCEL_HEADERS)
        products_sheet.append(
            [
                "Chocolate Cake",
                "cakes",
                "Rich chocolate cake",
                "Rich chocolate cake",
                "",
                "inherit",
                "false",
                "custom",
                "false",
                "true",
                "piece",
                "true",
                "false",
                "https://example.com/cake.jpg",
                "CAKE-001",
            ]
        )
        options_sheet = workbook.create_sheet("Options")
        options_sheet.append(PRODUCT_OPTION_EXCEL_HEADERS)
        options_sheet.append(["CAKE-001", "Small", "10", "true", "0"])
        options_sheet.append(["CAKE-001", "Large", "18", "false", "1"])

        for worksheet in (products_sheet, options_sheet):
            for column_cells in worksheet.columns:
                header = column_cells[0].value or ""
                worksheet.column_dimensions[column_cells[0].column_letter].width = max(len(header) + 4, 16)

        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="products-upload-template.xlsx"'
        return response


class ProductExcelUploadView(DashboardLocalizationMixin, StaffRequiredMixin, View):
    template_name = "dashboard/manage_products.html"

    def post(self, request, *args, **kwargs):
        language = self.get_language()
        dashboard_ui = get_dashboard_strings(language)
        redirect_target = request.POST.get("next") or "dashboard:products"
        if redirect_target not in {"dashboard:products", "dashboard:product-list"}:
            redirect_target = "dashboard:products"
        upload_form = ProductExcelUploadForm(request.POST, request.FILES, language=language)
        if not upload_form.is_valid():
            return self.render_upload_response(request, language, redirect_target, upload_form=upload_form)

        merge_duplicate_products_for_import()
        valid_rows, excel_errors = validate_product_excel_workbook(
            upload_form.cleaned_data["excel_file"],
            language,
        )
        if excel_errors:
            messages.error(
                request,
                dashboard_ui["excel_import_complete"].format(
                    created=0,
                    updated=0,
                    failed=len(excel_errors),
                ),
            )
            return self.render_upload_response(
                request,
                language,
                redirect_target,
                upload_form=upload_form,
                excel_errors=excel_errors,
            )

        created, updated = import_product_excel_rows(valid_rows)
        messages.success(
            request,
            dashboard_ui["excel_import_complete"].format(created=created, updated=updated, failed=0),
        )
        return redirect(redirect_target)

    def render_upload_response(self, request, language, redirect_target, upload_form=None, excel_errors=None):
        if redirect_target == "dashboard:product-list":
            context = get_product_list_context(language, upload_form=upload_form, excel_errors=excel_errors)
            return render(request, "dashboard/product_list.html", context)
        context = get_product_manage_context(language, upload_form=upload_form, excel_errors=excel_errors)
        return render(request, self.template_name, context)


class PromotionManageView(DashboardLocalizationMixin, StaffRequiredMixin, CreateView):
    template_name = "dashboard/manage_promotions.html"
    form_class = PromotionForm
    success_url = reverse_lazy("dashboard:promotions")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.get_language()
        site_settings = get_active_site_settings() or get_dashboard_site_settings()
        items = localize_queryset(
            Promotion.objects.all(),
            language,
            ["title", "subtitle", "description", "badge_text", "cta_text"],
        )
        for item in items:
            set_promotion_display_price(item, language, site_settings)
        context["items"] = items
        return context

    def form_valid(self, form):
        messages.success(self.request, self.get_dashboard_ui()["promotion_saved"])
        return super().form_valid(form)


class PromotionUpdateView(DashboardLocalizationMixin, StaffRequiredMixin, UpdateView):
    model = Promotion
    form_class = PromotionForm
    template_name = "dashboard/form_page.html"
    success_url = reverse_lazy("dashboard:promotions")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_dashboard_ui()["edit_promotion"]
        return context

    def form_valid(self, form):
        messages.success(self.request, self.get_dashboard_ui()["promotion_updated"])
        return super().form_valid(form)


class PromotionDeleteView(DashboardLocalizationMixin, StaffRequiredMixin, DeleteView):
    model = Promotion
    success_url = reverse_lazy("dashboard:promotions")

    def post(self, request, *args, **kwargs):
        messages.success(request, self.get_dashboard_ui()["promotion_deleted"])
        return super().post(request, *args, **kwargs)


class DeliveryAreaManageView(DashboardLocalizationMixin, StaffRequiredMixin, CreateView):
    template_name = "dashboard/manage_delivery_areas.html"
    form_class = DeliveryAreaForm
    success_url = reverse_lazy("dashboard:delivery-areas")

    def get_sub_area_formset(self, data=None, instance=None):
        return DeliverySubAreaFormSet(
            data=data,
            instance=instance,
            prefix="subareas",
            form_kwargs={"language": self.get_language()},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_delivery_area_manage_context(self.get_language(), area_form=context.get("form")))
        context.setdefault("sub_area_formset", self.get_sub_area_formset())
        return context

    def has_configured_sub_area(self, sub_area_formset):
        for sub_area_form in sub_area_formset.forms:
            cleaned_data = getattr(sub_area_form, "cleaned_data", None) or {}
            if cleaned_data.get("DELETE"):
                continue
            if (cleaned_data.get("name") or "").strip() and cleaned_data.get("is_active"):
                return True
        return False

    def validate_sub_area_pricing(self, form, sub_area_formset):
        if not form.cleaned_data.get("has_sub_areas"):
            return True
        if self.has_configured_sub_area(sub_area_formset):
            return True
        form.add_error("has_sub_areas", self.get_dashboard_ui()["sub_area_pricing_requires_active_sub_area"])
        return False

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form, sub_area_formset=self.get_sub_area_formset(data=self.request.POST))
        )

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)

        sub_area_formset = self.get_sub_area_formset(data=request.POST, instance=form.instance)
        with transaction.atomic():
            if sub_area_formset.is_valid() and self.validate_sub_area_pricing(form, sub_area_formset):
                area = form.save()
                sub_area_formset.instance = area
                sub_area_formset.save()
                messages.success(self.request, self.get_dashboard_ui()["delivery_area_saved"])
                return redirect(self.success_url)
            transaction.set_rollback(True)

        return self.render_to_response(
            self.get_context_data(form=form, sub_area_formset=sub_area_formset)
        )


class DeliveryAreaExcelTemplateView(DashboardLocalizationMixin, StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        workbook = Workbook()
        areas_sheet = workbook.active
        areas_sheet.title = "Areas"
        areas_sheet.append(DELIVERY_AREA_EXCEL_HEADERS)
        areas_sheet.append(["Mezzeh", "true", "", "0", "true"])
        areas_sheet.append(["Malki", "false", "15000", "1", "true"])

        sub_areas_sheet = workbook.create_sheet("SubAreas")
        sub_areas_sheet.append(DELIVERY_SUB_AREA_EXCEL_HEADERS)
        sub_areas_sheet.append(["Mezzeh", "East Mezzeh", "12000", "0", "true"])
        sub_areas_sheet.append(["Mezzeh", "West Mezzeh", "15000", "1", "true"])

        for worksheet in (areas_sheet, sub_areas_sheet):
            for column_cells in worksheet.columns:
                header = column_cells[0].value or ""
                worksheet.column_dimensions[column_cells[0].column_letter].width = max(len(header) + 4, 16)

        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="delivery-areas-upload-template.xlsx"'
        return response


class DeliveryAreaExcelUploadView(DashboardLocalizationMixin, StaffRequiredMixin, View):
    template_name = "dashboard/manage_delivery_areas.html"

    def post(self, request, *args, **kwargs):
        language = self.get_language()
        dashboard_ui = get_dashboard_strings(language)
        upload_form = DeliveryAreaExcelUploadForm(request.POST, request.FILES, language=language)
        if not upload_form.is_valid():
            return self.render_upload_response(request, language, upload_form=upload_form)

        valid_rows, excel_errors = validate_delivery_area_excel_workbook(
            upload_form.cleaned_data["excel_file"],
            language,
        )
        if excel_errors:
            messages.error(
                request,
                dashboard_ui["delivery_area_excel_import_complete"].format(
                    created=0,
                    updated=0,
                    failed=len(excel_errors),
                ),
            )
            return self.render_upload_response(
                request,
                language,
                upload_form=upload_form,
                excel_errors=excel_errors,
            )

        created, updated = import_delivery_area_excel_rows(valid_rows)
        messages.success(
            request,
            dashboard_ui["delivery_area_excel_import_complete"].format(created=created, updated=updated, failed=0),
        )
        return redirect("dashboard:delivery-areas")

    def render_upload_response(self, request, language, upload_form=None, excel_errors=None):
        context = get_delivery_area_manage_context(language, upload_form=upload_form, excel_errors=excel_errors)
        context["sub_area_formset"] = DeliverySubAreaFormSet(prefix="subareas", form_kwargs={"language": language})
        return render(request, self.template_name, context)


class DeliveryAreaUpdateView(DashboardLocalizationMixin, StaffRequiredMixin, UpdateView):
    model = DeliveryArea
    form_class = DeliveryAreaForm
    template_name = "dashboard/delivery_area_form.html"
    success_url = reverse_lazy("dashboard:delivery-areas")

    def get_sub_area_formset(self, data=None):
        return DeliverySubAreaFormSet(
            data=data,
            instance=self.object,
            prefix="subareas",
            form_kwargs={"language": self.get_language()},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_dashboard_ui()["edit_delivery_area"]
        context.setdefault("sub_area_formset", self.get_sub_area_formset())
        return context

    def has_configured_sub_area(self, sub_area_formset):
        for sub_area_form in sub_area_formset.forms:
            cleaned_data = getattr(sub_area_form, "cleaned_data", None) or {}
            if cleaned_data.get("DELETE"):
                continue
            if (cleaned_data.get("name") or "").strip() and cleaned_data.get("is_active"):
                return True
        return False

    def validate_sub_area_pricing(self, form, sub_area_formset):
        if not form.cleaned_data.get("has_sub_areas"):
            return True
        if self.has_configured_sub_area(sub_area_formset):
            return True
        form.add_error("has_sub_areas", self.get_dashboard_ui()["sub_area_pricing_requires_active_sub_area"])
        return False

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        sub_area_formset = self.get_sub_area_formset(data=request.POST)
        if (
            not form.is_valid()
            or not sub_area_formset.is_valid()
            or not self.validate_sub_area_pricing(form, sub_area_formset)
        ):
            return self.render_to_response(
                self.get_context_data(form=form, sub_area_formset=sub_area_formset)
            )

        try:
            with transaction.atomic():
                form.save()
                sub_area_formset.save()
        except ProtectedError:
            messages.error(request, self.get_dashboard_ui()["delivery_sub_area_in_use"])
            return self.render_to_response(
                self.get_context_data(form=form, sub_area_formset=sub_area_formset)
            )

        messages.success(self.request, self.get_dashboard_ui()["delivery_area_updated"])
        return redirect(self.success_url)


class DeliveryAreaDeleteView(DashboardLocalizationMixin, StaffRequiredMixin, DeleteView):
    model = DeliveryArea
    success_url = reverse_lazy("dashboard:delivery-areas")

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, self.get_dashboard_ui()["delivery_area_in_use"])
            return redirect("dashboard:delivery-areas")
        messages.success(request, self.get_dashboard_ui()["delivery_area_deleted"])
        return response


class SiteSettingsManageView(DashboardLocalizationMixin, StaffRequiredMixin, UpdateView):
    template_name = "dashboard/form_page.html"
    form_class = SiteSettingsForm
    success_url = reverse_lazy("dashboard:settings")

    def get_object(self, queryset=None):
        return get_dashboard_site_settings()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_dashboard_ui()["store_settings"]
        return context

    def form_valid(self, form):
        messages.success(self.request, self.get_dashboard_ui()["settings_updated"])
        return super().form_valid(form)


class DollarPriceManageView(DashboardLocalizationMixin, StaffRequiredMixin, UpdateView):
    template_name = "dashboard/form_page.html"
    form_class = DollarPriceForm
    success_url = reverse_lazy("dashboard:dollar-price")

    def get_object(self, queryset=None):
        return get_dashboard_site_settings()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_dashboard_ui()["edit_dollar_price"]
        context["submit_label"] = self.get_dashboard_ui()["save_dollar_price"]
        return context

    def form_valid(self, form):
        messages.success(self.request, self.get_dashboard_ui()["dollar_price_updated"])
        return super().form_valid(form)
