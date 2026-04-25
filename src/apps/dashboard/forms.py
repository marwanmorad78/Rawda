from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory

from apps.catalog.models import Category, Product
from apps.core.models import DeliveryArea, DeliverySubArea, SiteSettings
from apps.dashboard.localization import (
    get_dashboard_strings,
    get_field_label,
    get_field_placeholder,
)
from apps.promotions.models import Promotion


class DashboardLocalizedFormMixin:
    def __init__(self, *args, language="en", **kwargs):
        self.language = language
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            label = get_field_label(field_name, self.language)
            if label:
                field.label = label
            placeholder = get_field_placeholder(field_name, self.language)
            if placeholder:
                field.widget.attrs["placeholder"] = placeholder


class ManagerLoginForm(DashboardLocalizedFormMixin, AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Manager username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))


class CategoryForm(DashboardLocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "name",
            "description",
            "display_order",
            "is_active",
            "sold_by_weight",
            "is_price_linked_to_dollar",
            "cover_image",
            "external_image_url",
        ]


class ProductForm(DashboardLocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "short_description",
            "description",
            "price",
            "price_link_mode",
            "is_price_linked_to_dollar",
            "unit_label",
            "sold_by_weight_mode",
            "sold_by_weight",
            "is_available",
            "is_featured",
            "primary_image",
            "external_image_url",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "category" in self.fields and self.language == "ar":
            self.fields["category"].label_from_instance = lambda obj: obj.name_ar or obj.name
        self.fields["is_price_linked_to_dollar"].help_text = (
            "Used only when dollar price behavior is set to custom."
        )
        self.fields["sold_by_weight"].help_text = (
            "Used only when kilo sale behavior is set to custom."
        )


class PromotionForm(DashboardLocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = Promotion
        fields = [
            "description",
            "price",
            "is_price_linked_to_dollar",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = True

    def save(self, commit=True):
        promotion = super().save(commit=False)
        promotion.title = " ".join((promotion.description or "").strip().split())[:140] or "Promotion"
        if commit:
            promotion.save()
        return promotion


class SiteSettingsForm(DashboardLocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "store_name",
            "tagline",
            "about_text",
            "address",
            "primary_phone",
            "secondary_phone",
            "email",
            "working_hours_summary",
            "hero_title",
            "hero_subtitle",
            "hero_cta_text",
            "hero_cta_url",
            "is_active",
        ]


class DollarPriceForm(DashboardLocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ["dollar_price"]


class DeliveryAreaForm(DashboardLocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = DeliveryArea
        fields = ["name", "has_sub_areas", "delivery_fee", "display_order", "is_active"]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("has_sub_areas"):
            cleaned_data["delivery_fee"] = 0
        return cleaned_data

    def save(self, commit=True):
        area = super().save(commit=False)
        if self.cleaned_data.get("has_sub_areas"):
            area.delivery_fee = 0
        if commit:
            area.save()
        return area


class DeliverySubAreaForm(DashboardLocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = DeliverySubArea
        fields = ["name", "delivery_fee", "display_order", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Sub-area name" if self.language == "en" else "اسم المنطقة الفرعية"
        self.fields["delivery_fee"].label = "Sub-area fee" if self.language == "en" else "رسم المنطقة الفرعية"
        self.fields["display_order"].label = "Sub-area order" if self.language == "en" else "ترتيب المنطقة الفرعية"
        self.fields["is_active"].label = "Sub-area active" if self.language == "en" else "تفعيل المنطقة الفرعية"


DeliverySubAreaFormSet = inlineformset_factory(
    DeliveryArea,
    DeliverySubArea,
    form=DeliverySubAreaForm,
    extra=1,
    can_delete=True,
)
