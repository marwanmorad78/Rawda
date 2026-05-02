import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q
from django.utils.text import slugify

from apps.core.localization import DEFAULT_LANGUAGE, get_ui_strings
from apps.core.models import CustomerAddress, CustomerProfile, DeliveryArea, DeliverySubArea


SYRIA_COUNTRY_CODE = "963"
SYRIA_MOBILE_NUMBER_RE = re.compile(r"^9\d{8}$")
ARABIC_NAME_RE = re.compile(r"^[\u0621-\u064A\u064B-\u065F]+(?:\s+[\u0621-\u064A\u064B-\u065F]+)*$")


def normalize_phone_number(value):
    digits = re.sub(r"\D+", "", value or "")
    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith(SYRIA_COUNTRY_CODE):
        digits = digits[len(SYRIA_COUNTRY_CODE):]
    if len(digits) == 10 and digits.startswith("0"):
        digits = digits[1:]
    return digits


def validate_syrian_phone_number(value, error_message):
    phone_number = normalize_phone_number(value)
    if not SYRIA_MOBILE_NUMBER_RE.fullmatch(phone_number):
        raise forms.ValidationError(error_message)
    return phone_number


def phone_number_exists(phone_number, exclude_profile_pk=None):
    normalized_phone = normalize_phone_number(phone_number)
    if not normalized_phone:
        return False

    profile_queryset = CustomerProfile.objects.all()
    if exclude_profile_pk is not None:
        profile_queryset = profile_queryset.exclude(pk=exclude_profile_pk)

    for stored_phone in profile_queryset.values_list("phone_number", flat=True):
        if normalize_phone_number(stored_phone) == normalized_phone:
            return True

    legacy_users = get_user_model().objects.filter(customer_profile__isnull=True)
    for username in legacy_users.values_list("username", flat=True):
        if normalize_phone_number(username) == normalized_phone:
            return True

    return False


def find_user_by_phone_number(phone_number):
    normalized_phone = normalize_phone_number(phone_number)
    if not normalized_phone:
        return None

    for profile in CustomerProfile.objects.select_related("user"):
        if normalize_phone_number(profile.phone_number) == normalized_phone:
            return profile.user

    for user in get_user_model().objects.filter(customer_profile__isnull=True):
        if normalize_phone_number(user.username) == normalized_phone:
            return user

    return None


def generate_customer_username(full_name):
    user_model = get_user_model()
    base_slug = slugify(full_name or "")[:20] or "customer"
    candidate = base_slug
    suffix = 2
    while user_model.objects.filter(username__iexact=candidate).exists():
        trimmed_base = base_slug[: max(1, 20 - len(str(suffix)) - 1)]
        candidate = f"{trimmed_base}-{suffix}"
        suffix += 1
    return candidate


class LocalizedCustomerFormMixin:
    def __init__(self, *args, language=DEFAULT_LANGUAGE, **kwargs):
        self.language = language
        self.ui = get_ui_strings(language)
        super().__init__(*args, **kwargs)
        self.apply_localized_labels()

    def apply_localized_labels(self):
        label_map = {
            "full_name": "full_name",
            "username": "phone_number",
            "phone_number": "phone_number",
            "area": "area_name",
            "sub_area": "sub_area",
            "street_address": "street_address",
            "building": "building",
            "floor": "floor",
            "apartment": "apartment",
            "nearby_landmark": "nearby_landmark",
            "notes": "notes",
            "password": "password",
            "password1": "password",
            "password2": "confirm_password",
            "is_default": "default_address",
        }
        placeholder_map = {
            "full_name": "full_name_placeholder",
            "username": "phone_number_placeholder",
            "phone_number": "phone_number_placeholder",
            "street_address": "street_address_placeholder",
            "sub_area": "sub_area_placeholder",
            "building": "building_placeholder",
            "floor": "floor_placeholder",
            "apartment": "apartment_placeholder",
            "nearby_landmark": "nearby_landmark_placeholder",
            "notes": "notes_placeholder",
        }

        for field_name, field in self.fields.items():
            label_key = label_map.get(field_name)
            if label_key:
                field.label = self.ui[label_key]
            placeholder_key = placeholder_map.get(field_name)
            if placeholder_key and hasattr(field.widget, "attrs"):
                field.widget.attrs.setdefault("placeholder", self.ui[placeholder_key])
            if field_name in {"username", "phone_number"} and hasattr(field.widget, "attrs"):
                field.widget.attrs.update(
                    {
                        "autocomplete": "tel-national",
                        "data-syrian-phone-input": "true",
                        "dir": "ltr",
                        "inputmode": "numeric",
                        "style": "flex:1 1 auto;min-width:0;border:0;border-radius:0;background:transparent;box-shadow:none;padding-inline-start:0.8rem;padding-inline-end:1rem;text-align:left;",
                    }
                )


class DeliverySubAreaSelectionMixin:
    sub_area_field_name = "sub_area"
    area_field_name = "area"

    def configure_sub_area_field(self):
        sub_area_field = self.fields.get(self.sub_area_field_name)
        if not sub_area_field:
            return

        sub_area_field.queryset = DeliverySubArea.objects.none()
        sub_area_field.required = False
        sub_area_field.empty_label = self.ui["sub_area_placeholder"]
        sub_area_field.widget.attrs.update(
            {
                "data-delivery-sub-area-select": "true",
                "data-placeholder": self.ui["sub_area_placeholder"],
            }
        )
        area_field = self.fields.get(self.area_field_name)
        if area_field:
            area_field.widget.attrs["data-delivery-area-select"] = "true"

        area_value = None
        if self.is_bound:
            area_value = self.data.get(self.add_prefix(self.area_field_name)) or self.data.get(self.area_field_name)
        elif self.initial.get(self.area_field_name):
            area_value = self.initial.get(self.area_field_name)
        elif getattr(self.instance, "area_id", None):
            area_value = self.instance.area_id

        if hasattr(area_value, "pk"):
            area_value = area_value.pk

        current_sub_area_id = getattr(self.instance, "sub_area_id", None)
        if area_value:
            selected_area = DeliveryArea.objects.filter(pk=area_value).only("has_sub_areas").first()
            if selected_area is not None and selected_area.has_sub_areas:
                sub_area_field.queryset = DeliverySubArea.objects.filter(area_id=area_value).filter(
                    Q(is_active=True) | Q(pk=current_sub_area_id)
                )
            elif current_sub_area_id:
                sub_area_field.queryset = DeliverySubArea.objects.filter(area_id=area_value).filter(
                    Q(pk=current_sub_area_id)
                )
        elif current_sub_area_id:
            sub_area_field.queryset = DeliverySubArea.objects.filter(area_id=self.instance.area_id)

    def clean_sub_area_selection(self, cleaned_data):
        area = cleaned_data.get(self.area_field_name)
        sub_area = cleaned_data.get(self.sub_area_field_name)
        if not area:
            return cleaned_data

        if area.has_sub_areas:
            if sub_area is None:
                self.add_error(self.sub_area_field_name, self.ui["sub_area_required"])
            elif sub_area.area_id != area.id or not sub_area.is_active:
                self.add_error(self.sub_area_field_name, self.ui["sub_area_invalid"])
        elif sub_area is not None and (sub_area.area_id != area.id or not sub_area.is_active):
            self.add_error(self.sub_area_field_name, self.ui["sub_area_invalid"])

        return cleaned_data


class CustomerRegistrationForm(DeliverySubAreaSelectionMixin, LocalizedCustomerFormMixin, UserCreationForm):
    full_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=30)
    area = forms.ModelChoiceField(queryset=DeliveryArea.objects.none(), empty_label=None)
    sub_area = forms.ModelChoiceField(queryset=DeliverySubArea.objects.none(), required=False)
    street_address = forms.CharField(max_length=255)
    building = forms.CharField(max_length=80, required=False)
    floor = forms.CharField(max_length=40, required=False)
    apartment = forms.CharField(max_length=40, required=False)
    nearby_landmark = forms.CharField(max_length=180, required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("full_name", "username", "area", "street_address", "building", "floor", "apartment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["area"].queryset = DeliveryArea.objects.filter(is_active=True)
        self.fields["area"].empty_label = self.ui["area_name_placeholder"]
        self.configure_sub_area_field()

    def clean_username(self):
        phone_number = validate_syrian_phone_number(self.cleaned_data["username"], self.ui["phone_number_invalid"])
        if phone_number_exists(phone_number):
            raise forms.ValidationError(self.ui["phone_number_taken"])
        return phone_number

    def clean_full_name(self):
        full_name = " ".join((self.cleaned_data.get("full_name") or "").split())
        if self.language == "ar" and full_name and not ARABIC_NAME_RE.fullmatch(full_name):
            raise forms.ValidationError(self.ui["full_name_arabic_only"])
        return full_name

    def clean(self):
        cleaned_data = super().clean()
        return self.clean_sub_area_selection(cleaned_data)

    def save(self, commit=True):
        user = super().save(commit=False)
        phone_number = self.cleaned_data["username"]
        full_name = self.cleaned_data["full_name"]
        user.username = generate_customer_username(full_name)
        user.first_name = full_name
        if commit:
            user.save()
            profile, _ = CustomerProfile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": full_name,
                    "phone_number": phone_number,
                },
            )
            CustomerAddress.objects.create(
                profile=profile,
                area=self.cleaned_data["area"],
                sub_area=self.cleaned_data.get("sub_area"),
                street_address=self.cleaned_data["street_address"],
                building=self.cleaned_data["building"],
                floor=self.cleaned_data["floor"],
                apartment=self.cleaned_data["apartment"],
                nearby_landmark=self.cleaned_data["nearby_landmark"],
                notes=self.cleaned_data["notes"],
                is_default=True,
            )
        return user


class CustomerLoginForm(LocalizedCustomerFormMixin, AuthenticationForm):
    username = forms.CharField(max_length=30)
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    def clean_username(self):
        return validate_syrian_phone_number(self.cleaned_data["username"], self.ui["phone_number_invalid"])

    def clean(self):
        phone_number = self.cleaned_data.get("username")
        mapped_user = find_user_by_phone_number(phone_number)
        if mapped_user is not None:
            self.cleaned_data["username"] = mapped_user.username
        return super().clean()


class CustomerProfileForm(LocalizedCustomerFormMixin, forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ["full_name", "phone_number"]

    def clean_phone_number(self):
        phone_number = validate_syrian_phone_number(
            self.cleaned_data["phone_number"],
            self.ui["phone_number_invalid"],
        )
        if phone_number_exists(phone_number, exclude_profile_pk=self.instance.pk):
            raise forms.ValidationError(self.ui["phone_number_taken"])
        return phone_number

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.phone_number = self.cleaned_data["phone_number"]
        profile.full_name = self.cleaned_data["full_name"]
        user = profile.user
        user.first_name = profile.full_name
        if commit:
            user.save()
            profile.save()
        return profile


class CustomerAddressForm(DeliverySubAreaSelectionMixin, LocalizedCustomerFormMixin, forms.ModelForm):
    class Meta:
        model = CustomerAddress
        fields = [
            "area",
            "sub_area",
            "street_address",
            "building",
            "floor",
            "apartment",
            "nearby_landmark",
            "notes",
            "is_default",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["area"].queryset = DeliveryArea.objects.filter(is_active=True)
        self.fields["area"].empty_label = self.ui["area_name_placeholder"]
        self.configure_sub_area_field()

    def clean(self):
        cleaned_data = super().clean()
        return self.clean_sub_area_selection(cleaned_data)

    def save(self, commit=True, profile=None):
        address = super().save(commit=False)
        if profile is not None:
            address.profile = profile
        if commit:
            address.save()
        return address
