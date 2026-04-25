from django.contrib import admin

from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "display_order",
        "sold_by_weight",
        "is_price_linked_to_dollar",
        "is_active",
        "updated_at",
    )
    list_editable = ("display_order", "sold_by_weight", "is_price_linked_to_dollar", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "price_link_mode",
        "sold_by_weight_mode",
        "is_available",
        "is_featured",
        "updated_at",
    )
    list_filter = ("category", "price_link_mode", "sold_by_weight_mode", "is_available", "is_featured")
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
