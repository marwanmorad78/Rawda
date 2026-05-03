from django.urls import path

from .views import (
    AboutView,
    ActiveOrderStatusView,
    CustomerAddressCreateView,
    CustomerAddressDeleteView,
    DeliverySubAreaListView,
    CustomerAddressUpdateView,
    CustomerLoginView,
    CustomerLogoutView,
    CustomerProfileUpdateView,
    CustomerSettingsView,
    HomeView,
    PreviousOrdersView,
    ReorderView,
    RegisterPhoneCheckView,
    RegisterView,
    SetLanguageView,
)

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("account/register/", RegisterView.as_view(), name="register"),
    path("account/register/check-phone/", RegisterPhoneCheckView.as_view(), name="register-check-phone"),
    path("account/login/", CustomerLoginView.as_view(), name="login"),
    path("account/logout/", CustomerLogoutView.as_view(), name="logout"),
    path("account/settings/", CustomerSettingsView.as_view(), name="settings"),
    path("account/settings/profile/", CustomerProfileUpdateView.as_view(), name="settings-profile"),
    path("account/settings/addresses/", CustomerAddressCreateView.as_view(), name="address-add"),
    path("account/settings/addresses/<int:pk>/edit/", CustomerAddressUpdateView.as_view(), name="address-edit"),
    path("account/settings/addresses/<int:pk>/delete/", CustomerAddressDeleteView.as_view(), name="address-delete"),
    path("delivery-areas/<int:area_id>/subareas/", DeliverySubAreaListView.as_view(), name="delivery-subareas"),
    path("orders/", PreviousOrdersView.as_view(), name="orders"),
    path("orders/active-status/", ActiveOrderStatusView.as_view(), name="active-order-status"),
    path("orders/<int:pk>/reorder/", ReorderView.as_view(), name="order-reorder"),
    path("language/", SetLanguageView.as_view(), name="set-language"),
]
