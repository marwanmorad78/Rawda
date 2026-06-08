from django.contrib import admin

from .models import Company, ProductCompany, ProductCompanyOption, Category, Product, ProductImage, ProductOption


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1
    fields = ("name", "price", "is_default", "is_available", "display_order")


class ProductCompanyInline(admin.TabularInline):
    model = ProductCompany
    extra = 1
    fields = ("company",)


class ProductCompanyOptionInline(admin.TabularInline):
    model = ProductCompanyOption
    extra = 1
    fields = ("name", "price", "is_available", "order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "indented_name",
        "parent",
        "category_kind",
        "display_order",
        "sold_by_weight",
        "is_price_linked_to_dollar",
        "is_active",
        "updated_at",
    )
    list_editable = ("display_order", "sold_by_weight", "is_price_linked_to_dollar", "is_active")
    list_filter = ("parent", "is_active", "sold_by_weight", "is_price_linked_to_dollar")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "name_ar", "slug", "parent__name", "parent__name_ar")
    fields = (
        "parent",
        "name",
        "name_ar",
        "slug",
        "description",
        "description_ar",
        "display_order",
        "is_active",
        "sold_by_weight",
        "is_price_linked_to_dollar",
        "cover_image",
        "external_image_url",
    )

    @admin.display(description="Category")
    def indented_name(self, obj):
        return f"— {obj.name}" if obj.parent_id else obj.name

    @admin.display(description="Type")
    def category_kind(self, obj):
        return "Subcategory" if obj.parent_id else "Parent"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "product_type",
        "has_options",
        "price_link_mode",
        "sold_by_weight_mode",
        "is_available",
        "is_featured",
        "updated_at",
    )
    list_filter = (
        "category",
        "product_type",
        "has_options",
        "price_link_mode",
        "sold_by_weight_mode",
        "is_available",
        "is_featured",
    )
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductOptionInline, ProductCompanyInline, ProductImageInline]


@admin.register(ProductCompany)
class ProductCompanyAdmin(admin.ModelAdmin):
    list_display = ("company", "product", "updated_at")
    list_filter = ("company__is_active", "product__category")
    search_fields = ("company__code", "company__name", "product__name", "product__name_ar")
    inlines = [ProductCompanyOptionInline]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "display_order", "is_active", "updated_at")
    list_editable = ("display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
