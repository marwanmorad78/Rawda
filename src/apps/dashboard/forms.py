from decimal import Decimal

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory

from apps.catalog.models import Category, Product, ProductOption
from apps.core.localization import DEFAULT_LANGUAGE
from apps.core.models import DeliveryArea, DeliverySubArea, SiteSettings
from apps.dashboard.localization import (
    get_dashboard_strings,
    get_field_label,
    get_field_placeholder,
)
from apps.promotions.models import Promotion


class DashboardLocalizedFormMixin:
    def __init__(self, *args, language=DEFAULT_LANGUAGE, **kwargs):
        self.language = language
        self.dashboard_ui = get_dashboard_strings(language)
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


class CustomerAccessPasswordForm(forms.Form):
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, language=DEFAULT_LANGUAGE, **kwargs):
        self.language = language
        self.dashboard_ui = get_dashboard_strings(language)
        super().__init__(*args, **kwargs)
        self.fields["password"].label = self.dashboard_ui["customers_access_password"]
        self.fields["password"].widget.attrs["placeholder"] = self.dashboard_ui["customers_access_password"]

    def clean_password(self):
        password = self.cleaned_data["password"]
        if password != "rawda2026":
            raise forms.ValidationError(self.dashboard_ui["customers_access_denied"])
        return password


class CustomerPasswordChangeForm(forms.Form):
    new_password = forms.CharField(strip=False, widget=forms.PasswordInput)
    confirm_password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, language=DEFAULT_LANGUAGE, **kwargs):
        self.language = language
        self.dashboard_ui = get_dashboard_strings(language)
        super().__init__(*args, **kwargs)
        self.fields["new_password"].label = self.dashboard_ui["new_password"]
        self.fields["confirm_password"].label = self.dashboard_ui["confirm_password"]

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("confirm_password", self.dashboard_ui["password_mismatch"])
        return cleaned_data


class OrderAcceptForm(forms.Form):
    expected_time_minutes = forms.IntegerField(min_value=1, max_value=240)

    def __init__(self, *args, language=DEFAULT_LANGUAGE, suggested_minutes=20, **kwargs):
        self.language = language
        self.dashboard_ui = get_dashboard_strings(language)
        super().__init__(*args, **kwargs)
        self.fields["expected_time_minutes"].label = self.dashboard_ui["expected_time_label"]
        self.fields["expected_time_minutes"].initial = suggested_minutes
        self.fields["expected_time_minutes"].widget.attrs.update(
            {
                "inputmode": "numeric",
                "placeholder": str(suggested_minutes),
            }
        )


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
            "has_options",
            "is_available",
            "is_featured",
            "primary_image",
            "external_image_url",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "category" in self.fields and self.language == "ar":
            self.fields["category"].label_from_instance = lambda obj: obj.name_ar or obj.name
        self.fields["price"].required = False
        self.fields["is_price_linked_to_dollar"].help_text = self.dashboard_ui["custom_dollar_help"]
        self.fields["sold_by_weight"].help_text = self.dashboard_ui["custom_kilo_help"]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("has_options"):
            cleaned_data["price"] = Decimal("0")
        elif cleaned_data.get("price") is None:
            self.add_error("price", self.fields["price"].error_messages["required"])
        return cleaned_data


class ProductExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label="",
        help_text="",
    )

    def __init__(self, *args, language=DEFAULT_LANGUAGE, **kwargs):
        self.language = language
        self.dashboard_ui = get_dashboard_strings(language)
        super().__init__(*args, **kwargs)
        self.fields["excel_file"].label = self.dashboard_ui["products_excel_file"]
        self.fields["excel_file"].help_text = self.dashboard_ui["products_excel_help"]

    def clean_excel_file(self):
        excel_file = self.cleaned_data["excel_file"]
        if not excel_file.name.lower().endswith(".xlsx"):
            raise forms.ValidationError(self.dashboard_ui["xlsx_only_error"])
        return excel_file


ProductOptionFormSet = inlineformset_factory(
    Product,
    ProductOption,
    fields=("name", "price", "is_default", "display_order"),
    extra=5,
    can_delete=True,
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


        if self.language == "ar":
            self.fields["name"].label = "اسم المنطقة الفرعية"
            self.fields["delivery_fee"].label = "رسم المنطقة الفرعية"
            self.fields["display_order"].label = "ترتيب المنطقة الفرعية"
            self.fields["is_active"].label = "تفعيل المنطقة الفرعية"


DeliverySubAreaFormSet = inlineformset_factory(
    DeliveryArea,
    DeliverySubArea,
    form=DeliverySubAreaForm,
    extra=1,
    can_delete=True,
)
