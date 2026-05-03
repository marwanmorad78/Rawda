from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView
from openpyxl import Workbook, load_workbook

from apps.catalog.models import Category, Product
from apps.core.localization import DEFAULT_LANGUAGE, localize_instance, localize_queryset
from apps.core.models import CustomerOrder, CustomerProfile, DeliveryArea, DeliverySubArea, SiteSettings
from apps.core.pricing import (
    get_active_site_settings,
    set_product_display_price,
    set_promotion_display_price,
)
from apps.dashboard.forms import (
    CategoryForm,
    CustomerAccessPasswordForm,
    CustomerPasswordChangeForm,
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
    "unit_label",
    "is_available",
    "is_featured",
    "external_image_url",
    "sku",
]
PRODUCT_EXCEL_REQUIRED_HEADERS = ["product_name", "category", "price"]
BOOLEAN_COLUMNS = ["is_price_linked_to_dollar", "sold_by_weight", "is_available", "is_featured"]
PRODUCT_MODE_COLUMNS = {
    "price_link_mode": {Product.BEHAVIOR_INHERIT, Product.BEHAVIOR_CUSTOM},
    "sold_by_weight_mode": {Product.BEHAVIOR_INHERIT, Product.BEHAVIOR_CUSTOM},
}


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
    return parsed, None


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
        "items": items,
        "upload_form": upload_form or ProductExcelUploadForm(language=language),
        "excel_errors": excel_errors or [],
        "search_query": search_query,
    }


def validate_product_excel_workbook(excel_file, language=DEFAULT_LANGUAGE):
    dashboard_ui = get_dashboard_strings(language)
    # Validate the entire workbook before importing so partial product batches are avoided.
    try:
        workbook = load_workbook(excel_file, read_only=True, data_only=True)
    except Exception:
        return [], [dashboard_ui["excel_read_error"]]

    rows = workbook.active.iter_rows(values_only=True)
    headers = [normalize_excel_header(value) for value in next(rows, [])]
    header_positions = {header: index for index, header in enumerate(headers) if header}
    missing_headers = [
        header for header in PRODUCT_EXCEL_REQUIRED_HEADERS if header not in header_positions
    ]
    if missing_headers:
        return [], [f"Missing required column: {', '.join(missing_headers)}"]

    category_lookup, duplicate_names = get_product_excel_category_lookup()
    valid_rows = []
    errors = []
    seen_import_keys = set()

    for row_number, row_values in enumerate(rows, start=2):
        row = {
            header: row_values[index] if index < len(row_values) else None
            for header, index in header_positions.items()
        }
        if not any(value not in (None, "") for value in row.values()):
            continue

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

        price, price_error = parse_excel_decimal(row.get("price"))
        if price_error:
            row_errors.append(f"price: {price_error}")

        parsed_booleans = {}
        for column in BOOLEAN_COLUMNS:
            default = column == "is_available"
            parsed_booleans[column], boolean_error = parse_excel_boolean(row.get(column), default)
            if boolean_error:
                row_errors.append(f"{column}: {boolean_error}")

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

        valid_rows.append(
            {
                "category": category,
                "name": product_name,
                "short_description": normalize_excel_text(row.get("short_description")),
                "description": normalize_excel_text(row.get("description")),
                "price": price,
                "price_link_mode": parsed_modes["price_link_mode"],
                "is_price_linked_to_dollar": parsed_booleans["is_price_linked_to_dollar"],
                "sold_by_weight_mode": parsed_modes["sold_by_weight_mode"],
                "sold_by_weight": parsed_booleans["sold_by_weight"],
                "unit_label": normalize_excel_text(row.get("unit_label")) or "per item",
                "is_available": parsed_booleans["is_available"],
                "is_featured": parsed_booleans["is_featured"],
                "external_image_url": normalize_excel_text(row.get("external_image_url")),
                "sku": sku,
            }
        )

    if not valid_rows and not errors:
        errors.append("The uploaded workbook has no product rows.")

    return valid_rows, errors


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


def import_product_excel_rows(valid_rows):
    # Existing products are matched by SKU when present, otherwise by category and product name.
    created = 0
    updated = 0
    now = timezone.now()

    with transaction.atomic():
        merge_duplicate_products_for_import()
        for row in valid_rows:
            existing_product = find_existing_product_for_import(row)
            if existing_product:
                update_data = row.copy()
                if not update_data["sku"]:
                    update_data.pop("sku")
                update_data["updated_at"] = now
                Product.objects.filter(pk=existing_product.pk).update(**update_data)
                updated += 1
                continue
            product = Product(**row)
            product.save()
            created += 1

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


CUSTOMER_ACCESS_SESSION_KEY = "dashboard_customer_access_granted"


def attach_dashboard_order_display(orders, language):
    return attach_orders_display(orders, get_dashboard_strings(language), language)


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
        context = super().get_context_data(**kwargs)
        orders = list(
            CustomerOrder.objects.select_related("profile", "address").prefetch_related("items").all()
        )
        context["orders"] = attach_dashboard_order_display(orders, self.get_language())
        suggested_minutes = suggested_expected_minutes()
        for order in context["orders"]:
            order.suggested_expected_minutes = suggested_minutes
        return context


class PendingOrdersView(DashboardLocalizationMixin, StaffRequiredMixin, TemplateView):
    template_name = "dashboard/pending_orders.html"

    def get_context_data(self, **kwargs):
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
        self.order = get_object_or_404(
            CustomerOrder.objects.select_related("profile", "address").prefetch_related("items"),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.get_language()
        context["order"] = attach_order_display(self.order, self.get_dashboard_ui(), language)
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

        order.status = CustomerOrder.STATUS_BEING_PREPARED
        order.expected_time_minutes = form.cleaned_data["expected_time_minutes"]
        order.accepted_at = timezone.now()
        order.save(update_fields=["status", "expected_time_minutes", "accepted_at", "updated_at"])
        messages.success(request, self.get_dashboard_ui()["order_accepted"])
        return redirect("dashboard:pending-order-detail", pk=order.pk)


class DashboardOrderAdvanceView(DashboardLocalizationMixin, StaffRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(CustomerOrder, pk=pk)
        if order.status == CustomerOrder.STATUS_WAITING_ACCEPT:
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
        worksheet = workbook.active
        worksheet.title = "Products"
        worksheet.append(PRODUCT_EXCEL_HEADERS)
        worksheet.append(
            [
                "Chocolate Cake",
                "cakes",
                "Rich chocolate cake",
                "Rich chocolate cake",
                "10.5",
                "inherit",
                "false",
                "custom",
                "false",
                "piece",
                "true",
                "false",
                "https://example.com/cake.jpg",
                "CAKE-001",
            ]
        )
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
        context.setdefault("sub_area_formset", self.get_sub_area_formset())
        context["items"] = DeliveryArea.objects.prefetch_related("sub_areas").all()
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
