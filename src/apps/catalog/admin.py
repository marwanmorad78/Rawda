from django.contrib import admin

from .models import Category, Product, ProductImage, ProductOption


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1
    fields = ("name", "price", "is_default", "display_order")


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
        "has_options",
        "price_link_mode",
        "sold_by_weight_mode",
        "is_available",
        "is_featured",
        "updated_at",
    )
    list_filter = (
        "category",
        "has_options",
        "price_link_mode",
        "sold_by_weight_mode",
        "is_available",
        "is_featured",
    )
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductOptionInline, ProductImageInline]
