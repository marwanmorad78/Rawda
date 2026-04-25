from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from apps.catalog.models import Category, Product
from apps.core.localization import localize_instance, localize_queryset
from apps.core.models import DeliveryArea, DeliverySubArea, SiteSettings
from apps.core.pricing import (
    get_active_site_settings,
    set_product_display_price,
    set_promotion_display_price,
)
from apps.dashboard.forms import (
    CategoryForm,
    DeliveryAreaForm,
    DeliverySubAreaFormSet,
    DollarPriceForm,
    ManagerLoginForm,
    ProductForm,
    PromotionForm,
    SiteSettingsForm,
)
from apps.dashboard.mixins import DashboardLocalizationMixin, StaffRequiredMixin
from apps.promotions.models import Promotion


def get_dashboard_site_settings():
    site_settings, _ = SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            "store_name": "Al Rawda Center",
            "about_text": "Update your store information here.",
            "address": "Damascus",
            "primary_phone": "+963-000-000-000",
            "hero_title": "Fresh products for every home",
        },
    )
    return site_settings


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
        return context


class CategoryManageView(DashboardLocalizationMixin, StaffRequiredMixin, CreateView):
    template_name = "dashboard/manage_categories.html"
    form_class = CategoryForm
    success_url = reverse_lazy("dashboard:categories")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.get_language()
        context["items"] = localize_queryset(
            Category.objects.all().order_by("display_order", "name"),
            language,
            ["name", "description"],
        )
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.get_language()
        site_settings = get_active_site_settings() or get_dashboard_site_settings()
        items = list(Product.objects.select_related("category").all().order_by("name"))
        for item in items:
            localize_instance(item.category, language, ["name", "description"])
            localize_instance(item, language, ["name", "short_description", "description", "unit_label"])
            set_product_display_price(item, language, site_settings)
        context["items"] = items
        return context

    def form_valid(self, form):
        messages.success(self.request, self.get_dashboard_ui()["product_saved"])
        return super().form_valid(form)


class ProductUpdateView(DashboardLocalizationMixin, StaffRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/form_page.html"
    success_url = reverse_lazy("dashboard:products")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_dashboard_ui()["edit_product"]
        return context

    def form_valid(self, form):
        messages.success(self.request, self.get_dashboard_ui()["product_updated"])
        return super().form_valid(form)


class ProductDeleteView(DashboardLocalizationMixin, StaffRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy("dashboard:products")

    def post(self, request, *args, **kwargs):
        messages.success(request, self.get_dashboard_ui()["product_deleted"])
        return super().post(request, *args, **kwargs)


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
