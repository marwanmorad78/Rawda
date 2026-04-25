from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView

from apps.catalog.models import Category, Product
from apps.core.forms import (
    CustomerAddressForm,
    CustomerLoginForm,
    CustomerProfileForm,
    CustomerRegistrationForm,
    phone_number_exists,
    normalize_phone_number,
)
from apps.core.localization import (
    format_price_range,
    format_syp,
    get_language,
    get_ui_strings,
    localize_instance,
    localize_queryset,
)
from apps.core.models import CustomerAddress, CustomerProfile, DeliveryArea, SiteSettings
from apps.core.pricing import set_product_display_price, set_promotion_display_price
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


class HomeView(TemplateView):
    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language(self.request)
        site_content = get_localized_site_content(language)
        context["site_content"] = site_content
        context["categories"] = localize_queryset(
            Category.objects.filter(is_active=True).order_by("display_order", "name"),
            language,
            ["name", "description"],
        )
        featured_products = list(
            Product.objects.filter(is_available=True, is_featured=True, category__is_active=True)
            .select_related("category")[:8]
        )
        for product in featured_products:
            localize_instance(product.category, language, ["name", "description"])
            localize_instance(
                product,
                language,
                ["name", "short_description", "description", "unit_label"],
            )
            set_product_display_price(product, language, site_content)
        context["featured_products"] = featured_products
        context["promotions"] = localize_queryset(
            Promotion.active(),
            language,
            ["title", "subtitle", "description", "badge_text", "cta_text"],
        )
        for promotion in context["promotions"]:
            set_promotion_display_price(promotion, language, site_content)
            promotion.add_to_cart_url = reverse("catalog:add-offer-to-cart", kwargs={"slug": promotion.slug})
        return context


class AboutView(TemplateView):
    template_name = "public/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_content"] = get_localized_site_content(get_language(self.request))
        return context


class RegisterView(CustomerContextMixin, FormView):
    template_name = "public/register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("core:settings")

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
        return self.get_redirect_url() or str(reverse_lazy("core:settings"))


class CustomerLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


class CustomerSettingsView(CustomerContextMixin, LoginRequiredMixin, TemplateView):
    template_name = "public/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_customer_profile()
        context.setdefault("profile_form", CustomerProfileForm(instance=profile, language=self.get_language()))
        context.setdefault("address_form", CustomerAddressForm(language=self.get_language()))
        context["site_content"] = self.get_site_content()
        context["addresses"] = profile.addresses.select_related("area", "sub_area").all()
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
                "site_content": self.get_site_content(),
                "addresses": profile.addresses.select_related("area", "sub_area").all(),
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
                "site_content": self.get_site_content(),
                "addresses": profile.addresses.select_related("area", "sub_area").all(),
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
        orders = list(profile.orders.select_related("address__area", "address__sub_area").prefetch_related("items").all())
        for order in orders:
            order.display_total = format_price_range(order.total_min, order.total_max, language)
            order.display_delivery_fee = format_syp(order.delivery_fee, language)
            for item in order.items.all():
                item.display_line_total = format_price_range(item.line_total_min, item.line_total_max, language)
        context["orders"] = orders
        return context


class DeliverySubAreaListView(View):
    def get(self, request, area_id, *args, **kwargs):
        area = DeliveryArea.objects.filter(pk=area_id).prefetch_related("sub_areas").first()
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
        language = request.GET.get("lang", "en")
        if language in {"en", "ar"}:
            request.session["site_language"] = language
        return redirect(request.META.get("HTTP_REFERER", "core:home"))
