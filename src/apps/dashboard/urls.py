from django.urls import path

from .views import (
    CategoryDeleteView,
    CategoryManageView,
    CategoryUpdateView,
    DashboardHomeView,
    DeliveryAreaDeleteView,
    DeliveryAreaManageView,
    DeliveryAreaUpdateView,
    DollarPriceManageView,
    ManagerLoginView,
    ManagerLogoutView,
    ProductDeleteView,
    ProductExcelTemplateView,
    ProductExcelUploadView,
    ProductListView,
    ProductManageView,
    ProductUpdateView,
    PromotionDeleteView,
    PromotionManageView,
    PromotionUpdateView,
    SiteSettingsManageView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="index"),
    path("login/", ManagerLoginView.as_view(), name="login"),
    path("logout/", ManagerLogoutView.as_view(), name="logout"),
    path("categories/", CategoryManageView.as_view(), name="categories"),
    path("categories/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category-edit"),
    path("categories/<int:pk>/delete/", CategoryDeleteView.as_view(), name="category-delete"),
    path("products/", ProductManageView.as_view(), name="products"),
    path("products/list/", ProductListView.as_view(), name="product-list"),
    path("products/excel-template/", ProductExcelTemplateView.as_view(), name="product-excel-template"),
    path("products/upload-excel/", ProductExcelUploadView.as_view(), name="product-excel-upload"),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product-edit"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product-delete"),
    path("promotions/", PromotionManageView.as_view(), name="promotions"),
    path("promotions/<int:pk>/edit/", PromotionUpdateView.as_view(), name="promotion-edit"),
    path("promotions/<int:pk>/delete/", PromotionDeleteView.as_view(), name="promotion-delete"),
    path("delivery-areas/", DeliveryAreaManageView.as_view(), name="delivery-areas"),
    path("delivery-areas/<int:pk>/edit/", DeliveryAreaUpdateView.as_view(), name="delivery-area-edit"),
    path("delivery-areas/<int:pk>/delete/", DeliveryAreaDeleteView.as_view(), name="delivery-area-delete"),
    path("dollar-price/", DollarPriceManageView.as_view(), name="dollar-price"),
    path("settings/", SiteSettingsManageView.as_view(), name="settings"),
]
