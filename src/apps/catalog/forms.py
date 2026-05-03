from django import forms

from apps.core.localization import DEFAULT_LANGUAGE, get_ui_strings
from apps.core.models import CustomerAddress


class CheckoutAddressForm(forms.Form):
    address = forms.ModelChoiceField(
        queryset=CustomerAddress.objects.none(),
        widget=forms.Select,
        empty_label=None,
    )

    def __init__(self, *args, addresses=None, language=DEFAULT_LANGUAGE, **kwargs):
        self.ui = get_ui_strings(language)
        super().__init__(*args, **kwargs)
        self.fields["address"].label = self.ui.get("delivery_address", "Delivery address")
        if addresses is not None:
            self.fields["address"].queryset = addresses.filter(area__is_active=True)
        default_address = self.fields["address"].queryset.filter(is_default=True).first()
        if default_address is not None and not self.initial.get("address"):
            self.initial["address"] = default_address.pk
