from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.db.models import Q
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView

from apps.catalog.cart import (
    PRODUCT_ITEM_TYPE,
    PRODUCT_COMPANY_OPTION_ITEM_TYPE,
    PRODUCT_OPTION_ITEM_TYPE,
    PROMOTION_ITEM_TYPE,
    add_item,
    preserve_cart_for_next_request,
    set_checkout_service_type,
)
from apps.catalog.models import Category, Product, ProductCompany, ProductCompanyOption, ProductOption
from apps.catalog.sorting import sort_category_products
from apps.core.forms import (
    CustomerAddressForm,
    CustomerLoginForm,
    CustomerProfileForm,
    CustomerRegistrationForm,
    phone_number_exists,
    normalize_phone_number,
)
from apps.core.localization import (
    DEFAULT_LANGUAGE,
    get_language,
    get_ui_strings,
    localize_instance,
    localize_queryset,
)
from apps.core.models import CustomerAddress, CustomerOrder, CustomerProfile, DeliveryArea, SiteSettings
from apps.core.order_status import attach_order_display, attach_orders_display, get_active_customer_order
from apps.core.pricing import (
    product_is_sold_by_weight,
    set_product_display_price,
    set_promotion_display_price,
)
from apps.core.services import mark_order_cancelled, sync_center_status_and_auto_accept_waiting_orders
from apps.promotions.models import Promotion


def wants_json_response(request):
    accept_header = request.headers.get("Accept", "")
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in accept_header


def form_error_payload(form):
    field_errors = {
        field_name: [str(error) for error in field_errors]
        for field_name, field_errors in form.errors.items()
    }
    return {
        "field_errors": field_errors,
        "errors": [
            error
            for errors in field_errors.values()
            for error in errors
        ],
    }


def get_localized_site_content(language):
    return localize_instance(
        SiteSettings.objects.filter(is_active=True).first(),
        language,
        [
            "store_name",
            "tagline",
            "about_text",
            "address",
            "working_hours_summary",
            "hero_title",
            "hero_subtitle",
            "hero_cta_text",
        ],
    )


class CustomerContextMixin:
    login_url = reverse_lazy("core:login")

    def get_language(self):
        return get_language(self.request)

    def get_site_content(self):
        return get_localized_site_content(self.get_language())

    def get_customer_profile(self):
        defaults = {
            "full_name": self.request.user.first_name or self.request.user.username,
            "phone_number": self.request.user.username,
        }
        return CustomerProfile.objects.get_or_create(user=self.request.user, defaults=defaults)[0]

    def get_settings_addresses(self, edit_form=None):
        addresses = list(
            self.get_customer_profile().addresses.select_related("area", "sub_area").all()
        )
        for address in addresses:
            if edit_form is not None and edit_form.instance.pk == address.pk:
                address.edit_form = edit_form
            else:
                address.edit_form = CustomerAddressForm(
                    instance=address,
                    language=self.get_language(),
                )
        return addresses


class HomeView(TemplateView):
    template_name = "public/home.html"

    def get_home_categories(self, language, site_content):
        product_queryset = (
            Product.objects.all()
            .prefetch_related(
                "options",
                Prefetch(
                    "companies",
                    queryset=ProductCompany.objects.filter(company__is_active=True)
                    .select_related("company")
                    .prefetch_related(
                        Prefetch(
                            "options",
                            queryset=ProductCompanyOption.objects.order_by("order", "name", "id"),
                            to_attr="prefetched_options",
                        )
                    ),
                    to_attr="prefetched_companies",
                ),
            )
        )
        subcategory_queryset = Category.objects.filter(is_active=True).order_by("display_order", "name")
        categories = list(
            Category.objects.filter(is_active=True, parent__isnull=True)
            .order_by("display_order", "name")
            .prefetch_related(
                Prefetch("products", queryset=product_queryset, to_attr="home_products"),
                Prefetch("subcategories", queryset=subcategory_queryset, to_attr="home_subcategories"),
            )
        )
        for category in categories:
            localize_instance(category, language, ["name", "description"])
            for subcategory in category.home_subcategories:
                localize_instance(subcategory, language, ["name", "description"])
            if category.home_subcategories:
                category.home_products = []
                continue
            category.home_products = sort_category_products(category.home_products)[:8]
            for product in category.home_products:
                product.category = category
                if product.is_company_grouped:
                    product.prefetched_companies = list(getattr(product, "prefetched_companies", []))
                    for company in product.prefetched_companies:
                        company.product = product
                        for option in getattr(company, "prefetched_options", []):
                            option.company = company
                else:
                    product.prefetched_options = list(product.options.all())
                    for option in product.prefetched_options:
                        option.product = product
                localize_instance(product, language, ["name", "short_description", "description", "unit_label"])
                set_product_display_price(product, language, site_content)
        return categories

    def get_context_data(self, **kwargs):
        sync_center_status_and_auto_accept_waiting_orders()
        context = super().get_context_data(**kwargs)
        language = get_language(self.request)
        site_content = get_localized_site_content(language)
        context["site_content"] = site_content
        if self.request.user.is_authenticated:
            customer_name = (self.request.user.first_name or self.request.user.username or "").strip()
            context["customer_first_name"] = customer_name.split()[0] if customer_name else ""
            profile, _ = CustomerProfile.objects.get_or_create(
                user=self.request.user,
                defaults={
                    "full_name": self.request.user.first_name or self.request.user.username,
                    "phone_number": self.request.user.username,
                },
            )
            active_order = get_active_customer_order(profile)
            context["active_order"] = (
                attach_order_display(active_order, get_ui_strings(language), language) if active_order else None
            )
            context["active_order_status_url"] = reverse("catalog:cart")
        context["categories"] = self.get_home_categories(language, site_content)
        context["promotions"] = localize_queryset(
            Promotion.active(),
            language,
            ["title", "subtitle", "description", "badge_text", "cta_text"],
        )
        for promotion in context["promotions"]:
            set_promotion_display_price(promotion, language, site_content)
            promotion.add_to_cart_url = reverse("catalog:add-offer-to-cart", kwargs={"slug": promotion.slug})
        return context


class ActiveOrderStatusView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        sync_center_status_and_auto_accept_waiting_orders()
        language = get_language(request)
        profile, _ = CustomerProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "full_name": request.user.first_name or request.user.username,
                "phone_number": request.user.username,
            },
        )
        active_order = get_active_customer_order(profile)
        if active_order is None:
            return JsonResponse({"has_active_order": False, "html": ""})

        order = attach_order_display(active_order, get_ui_strings(language), language)
        html = render_to_string(
            "partials/order_status_tracker.html",
            {
                "order": order,
                "labels": get_ui_strings(language),
                "heading": get_ui_strings(language)["active_order_heading"],
                "action_url": reverse("catalog:cart"),
                "action_label": get_ui_strings(language)["view_order"],
                "allow_customer_cancel": True,
            },
            request=request,
        )
        return JsonResponse({"has_active_order": True, "html": html})


class AboutView(TemplateView):
    template_name = "public/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_content"] = get_localized_site_content(get_language(self.request))
        return context


class RegisterView(CustomerContextMixin, FormView):
    template_name = "public/register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("core:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:settings")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["language"] = self.get_language()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_content"] = self.get_site_content()
        return context

    def form_valid(self, form):
        user = form.save()
        authenticated_user = authenticate(
            self.request,
            username=user.username,
            password=form.cleaned_data["password1"],
        )
        if authenticated_user is not None:
            login(self.request, authenticated_user)
        messages.success(self.request, get_ui_strings(self.get_language())["account_created"])
        if wants_json_response(self.request):
            return JsonResponse({"ok": True, "redirect_url": str(self.get_success_url())})
        return super().form_valid(form)

    def form_invalid(self, form):
        if wants_json_response(self.request):
            payload = {"ok": False}
            payload.update(form_error_payload(form))
            return JsonResponse(payload, status=400)
        return super().form_invalid(form)


class RegisterPhoneCheckView(View):
    def get(self, request, *args, **kwargs):
        phone_number = normalize_phone_number(request.GET.get("phone", ""))
        exists = bool(phone_number) and phone_number_exists(phone_number)
        return JsonResponse({"exists": exists})


class CustomerLoginView(CustomerContextMixin, LoginView):
    template_name = "public/login.html"
    authentication_form = CustomerLoginForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:settings")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["language"] = self.get_language()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_content"] = self.get_site_content()
        return context

    def form_valid(self, form):
        messages.success(self.request, get_ui_strings(self.get_language())["login_success"])
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_redirect_url() or str(reverse_lazy("core:home"))


class CustomerLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


class CustomerSettingsView(CustomerContextMixin, LoginRequiredMixin, TemplateView):
    template_name = "public/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_customer_profile()
        context.setdefault("profile_form", CustomerProfileForm(instance=profile, language=self.get_language()))
        context.setdefault("address_form", CustomerAddressForm(language=self.get_language()))
        context.setdefault("is_address_modal_open", False)
        context.setdefault("open_edit_address_id", None)
        context["site_content"] = self.get_site_content()
        context["addresses"] = self.get_settings_addresses()
        return context


class CustomerProfileUpdateView(CustomerContextMixin, LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        profile = self.get_customer_profile()
        profile_form = CustomerProfileForm(
            request.POST,
            instance=profile,
            language=self.get_language(),
        )
        address_form = CustomerAddressForm(language=self.get_language())
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, get_ui_strings(self.get_language())["profile_updated"])
            return redirect("core:settings")
        return render(
            request,
            "public/settings.html",
            {
                "profile_form": profile_form,
                "address_form": address_form,
                "is_address_modal_open": False,
                "open_edit_address_id": None,
                "site_content": self.get_site_content(),
                "addresses": self.get_settings_addresses(),
            },
        )


class CustomerAddressCreateView(CustomerContextMixin, LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        profile = self.get_customer_profile()
        address_form = CustomerAddressForm(request.POST, language=self.get_language())
        profile_form = CustomerProfileForm(instance=profile, language=self.get_language())
        if address_form.is_valid():
            address_form.save(profile=profile)
            messages.success(request, get_ui_strings(self.get_language())["address_added"])
            return redirect("core:settings")
        return render(
            request,
            "public/settings.html",
            {
                "profile_form": profile_form,
                "address_form": address_form,
                "is_address_modal_open": True,
                "open_edit_address_id": None,
                "site_content": self.get_site_content(),
                "addresses": self.get_settings_addresses(),
            },
        )


class CustomerAddressUpdateView(CustomerContextMixin, LoginRequiredMixin, UpdateView):
    model = CustomerAddress
    form_class = CustomerAddressForm
    template_name = "public/address_form.html"
    success_url = reverse_lazy("core:settings")

    def get_queryset(self):
        return self.get_customer_profile().addresses.all()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["language"] = self.get_language()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_content"] = self.get_site_content()
        return context

    def form_valid(self, form):
        messages.success(self.request, get_ui_strings(self.get_language())["address_updated"])
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(
            self.request,
            "public/settings.html",
            {
                "profile_form": CustomerProfileForm(
                    instance=self.get_customer_profile(),
                    language=self.get_language(),
                ),
                "address_form": CustomerAddressForm(language=self.get_language()),
                "is_address_modal_open": False,
                "open_edit_address_id": form.instance.pk,
                "site_content": self.get_site_content(),
                "addresses": self.get_settings_addresses(edit_form=form),
            },
        )


class CustomerAddressDeleteView(CustomerContextMixin, LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        address = get_object_or_404(self.get_customer_profile().addresses.all(), pk=pk)
        address.delete()
        remaining_addresses = self.get_customer_profile().addresses.all()
        if remaining_addresses.exists() and not remaining_addresses.filter(is_default=True).exists():
            first_address = remaining_addresses.first()
            if first_address is not None:
                first_address.is_default = True
                first_address.save(update_fields=["is_default"])
        messages.success(request, get_ui_strings(self.get_language())["address_deleted"])
        return redirect("core:settings")


class PreviousOrdersView(CustomerContextMixin, LoginRequiredMixin, TemplateView):
    template_name = "public/orders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_content"] = self.get_site_content()
        profile = self.get_customer_profile()
        context["profile"] = profile
        language = self.get_language()
        orders = list(
            profile.orders.select_related("address__area", "address__sub_area")
            .prefetch_related("items")
            .filter(status=CustomerOrder.STATUS_DONE)
        )
        attach_orders_display(orders, get_ui_strings(language), language)
        context["orders"] = orders
        return context


class CancelOrderView(CustomerContextMixin, LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        profile = self.get_customer_profile()
        order = get_object_or_404(
            profile.orders.select_for_update(),
            pk=pk,
        )
        ui = get_ui_strings(self.get_language())
        if not order.can_customer_cancel:
            messages.error(request, ui["order_cancel_unavailable"])
            return redirect("catalog:cart")

        mark_order_cancelled(order)
        messages.success(request, ui["order_cancelled_success"])
        return redirect("catalog:cart")


class ReorderView(CustomerContextMixin, LoginRequiredMixin, View):
    def target_is_weight_based(self, item_type, item_id):
        if item_type == PRODUCT_ITEM_TYPE:
            product = Product.objects.select_related("category", "category__parent").filter(pk=item_id).first()
        elif item_type == PRODUCT_OPTION_ITEM_TYPE:
            option = (
                ProductOption.objects.select_related("product__category", "product__category__parent")
                .filter(pk=item_id)
                .first()
            )
            product = option.product if option else None
        elif item_type == PRODUCT_COMPANY_OPTION_ITEM_TYPE:
            option = (
                ProductCompanyOption.objects.select_related(
                    "company__product__category",
                    "company__product__category__parent",
                )
                .filter(pk=item_id)
                .first()
            )
            product = option.company.product if option else None
        else:
            product = None
        return bool(product and product_is_sold_by_weight(product))

    def resolve_order_item(self, item):
        if item.cart_item_id:
            if item.item_type == PRODUCT_ITEM_TYPE:
                exists = Product.objects.filter(
                    pk=item.cart_item_id,
                    product_type=Product.PRODUCT_TYPE_NORMAL,
                    is_available=True,
                    category__is_active=True,
                    has_options=False,
                ).exists()
                return (PRODUCT_ITEM_TYPE, item.cart_item_id) if exists else None
            if item.item_type == PRODUCT_OPTION_ITEM_TYPE:
                exists = ProductOption.objects.filter(
                    pk=item.cart_item_id,
                    product__product_type=Product.PRODUCT_TYPE_NORMAL,
                    product__is_available=True,
                    product__category__is_active=True,
                ).exists()
                return (PRODUCT_OPTION_ITEM_TYPE, item.cart_item_id) if exists else None
            if item.item_type == PRODUCT_COMPANY_OPTION_ITEM_TYPE:
                exists = ProductCompanyOption.objects.filter(
                    pk=item.cart_item_id,
                    is_available=True,
                    company__company__is_active=True,
                    company__product__product_type=Product.PRODUCT_TYPE_COMPANY_GROUPED,
                    company__product__is_available=True,
                    company__product__category__is_active=True,
                ).exists()
                return (PRODUCT_COMPANY_OPTION_ITEM_TYPE, item.cart_item_id) if exists else None
            if item.item_type == PROMOTION_ITEM_TYPE:
                exists = Promotion.active().filter(pk=item.cart_item_id).exists()
                return (PROMOTION_ITEM_TYPE, item.cart_item_id) if exists else None

        title = (item.title or "").strip()
        if not title:
            return None

        if item.item_type == PRODUCT_ITEM_TYPE:
            product = Product.objects.filter(
                Q(name__iexact=title) | Q(name_ar__iexact=title),
                product_type=Product.PRODUCT_TYPE_NORMAL,
                is_available=True,
                category__is_active=True,
                has_options=False,
            ).first()
            return (PRODUCT_ITEM_TYPE, product.pk) if product else None

        if item.item_type == PRODUCT_OPTION_ITEM_TYPE:
            product_title, _, option_name = title.partition(" - ")
            option_query = ProductOption.objects.filter(
                product__is_available=True,
                product__category__is_active=True,
            )
            if option_name:
                product_title = product_title.strip()
                option_query = option_query.filter(name__iexact=option_name.strip()).filter(
                    Q(product__name__iexact=product_title) | Q(product__name_ar__iexact=product_title)
                )
            else:
                option_query = option_query.filter(name__iexact=title)
            option = option_query.first()
            return (PRODUCT_OPTION_ITEM_TYPE, option.pk) if option else None

        if item.item_type == PRODUCT_COMPANY_OPTION_ITEM_TYPE:
            option_query = ProductCompanyOption.objects.filter(
                is_available=True,
                company__company__is_active=True,
                company__product__product_type=Product.PRODUCT_TYPE_COMPANY_GROUPED,
                company__product__is_available=True,
                company__product__category__is_active=True,
            )
            if item.selected_option_label:
                option_query = option_query.filter(name__iexact=item.selected_option_label.strip())
            if item.company_label:
                option_query = option_query.filter(
                    company__company__name__iexact=item.company_label.strip()
                )
            if title:
                option_query = option_query.filter(
                    Q(company__product__name__iexact=title) | Q(company__product__name_ar__iexact=title)
                )
            option = option_query.first()
            return (PRODUCT_COMPANY_OPTION_ITEM_TYPE, option.pk) if option else None

        if item.item_type == PROMOTION_ITEM_TYPE:
            promotion = Promotion.active().filter(Q(title__iexact=title) | Q(title_ar__iexact=title)).first()
            return (PROMOTION_ITEM_TYPE, promotion.pk) if promotion else None

        return None

    def post(self, request, pk, *args, **kwargs):
        profile = self.get_customer_profile()
        order = get_object_or_404(profile.orders.prefetch_related("items"), pk=pk)
        added_count = 0

        for item in order.items.all():
            target = self.resolve_order_item(item)
            if target is None:
                continue
            item_type, item_id = target
            is_weight_based = self.target_is_weight_based(item_type, item_id)
            quantity = item.quantity if is_weight_based else max(item.quantity, 1)
            try:
                add_item(
                    request,
                    item_type,
                    item_id,
                    quantity,
                    is_weight_based=is_weight_based,
                )
            except ValueError:
                continue
            added_count += 1

        ui = get_ui_strings(self.get_language())
        if added_count:
            set_checkout_service_type(request, order.service_type)
            preserve_cart_for_next_request(request)
            messages.success(request, ui["reorder_added"])
        else:
            messages.warning(request, ui["reorder_unavailable"])
        return redirect("catalog:cart")


class DeliverySubAreaListView(View):
    def get(self, request, area_id, *args, **kwargs):
        area = DeliveryArea.objects.filter(pk=area_id, is_active=True).prefetch_related("sub_areas").first()
        if area is None:
            return JsonResponse({"sub_areas": []}, status=404)
        if not area.has_sub_areas:
            return JsonResponse({"sub_areas": []})

        items = list(
            area.sub_areas.filter(is_active=True).values("id", "name")
        )
        return JsonResponse({"sub_areas": items})


class SetLanguageView(View):
    def get(self, request, *args, **kwargs):
        language = request.GET.get("lang", DEFAULT_LANGUAGE)
        if language in {"en", "ar"}:
            request.session["site_language"] = language
        return redirect(request.META.get("HTTP_REFERER", "core:home"))
