from django.urls import path

from .views import (
    AddOfferToCartView,
    AddToCartView,
    CartDetailView,
    CartRemoveView,
    CartUpdateView,
    CategoryDetailView,
    CheckoutAddressView,
    CheckoutConfirmView,
    CheckoutServiceView,
    InvoiceView,
    ProductDetailView,
)

app_name = "catalog"

urlpatterns = [
    path("cart/", CartDetailView.as_view(), name="cart"),
    path("checkout/service/", CheckoutServiceView.as_view(), name="checkout-service"),
    path("checkout/address/", CheckoutAddressView.as_view(), name="checkout-address"),
    path("invoice/", InvoiceView.as_view(), name="invoice"),
    path("checkout/confirm/", CheckoutConfirmView.as_view(), name="checkout-confirm"),
    path("products/<slug:slug>/add-to-cart/", AddToCartView.as_view(), name="add-to-cart"),
    path("offers/<slug:slug>/add-to-cart/", AddOfferToCartView.as_view(), name="add-offer-to-cart"),
    path("cart/items/<str:item_type>/<int:item_id>/update/", CartUpdateView.as_view(), name="cart-update"),
    path("cart/items/<str:item_type>/<int:item_id>/remove/", CartRemoveView.as_view(), name="cart-remove"),
    path("categories/<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
]
