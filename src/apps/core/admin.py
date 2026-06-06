from django.contrib import admin

from .models import (
    CenterStatus,
    CustomerAddress,
    CustomerOrder,
    CustomerOrderItem,
    DeliveryArea,
    DeliverySubArea,
    SiteSettings,
)


class CustomerOrderItemInline(admin.TabularInline):
    model = CustomerOrderItem
    extra = 0
    readonly_fields = (
        "item_type",
        "title",
        "company_label",
        "selected_option_label",
        "display_quantity",
        "unit_price",
        "line_total_min",
        "line_total_max",
    )
    fields = readonly_fields
    can_delete = False

    @admin.display(description="Quantity")
    def display_quantity(self, obj):
        from apps.core.localization import format_quantity

        return format_quantity(obj.quantity, obj.is_weight_based, "en")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("store_name", "primary_phone", "is_active", "updated_at")


@admin.register(DeliveryArea)
class DeliveryAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "has_sub_areas", "delivery_fee", "display_order", "is_active", "updated_at")
    list_editable = ("has_sub_areas", "delivery_fee", "display_order", "is_active")
    search_fields = ("name",)


@admin.register(DeliverySubArea)
class DeliverySubAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "area", "delivery_fee", "display_order", "is_active", "updated_at")
    list_filter = ("area", "is_active")
    list_editable = ("delivery_fee", "display_order", "is_active")
    search_fields = ("name", "area__name")


@admin.register(CenterStatus)
class CenterStatusAdmin(admin.ModelAdmin):
    list_display = ("status", "busy_until", "updated_by", "updated_at")
    list_filter = ("status",)


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("profile", "area", "sub_area", "street_address", "is_default", "updated_at")
    list_filter = ("area", "sub_area", "is_default")
    search_fields = ("profile__full_name", "street_address", "building", "nearby_landmark")


@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "profile",
        "service_type",
        "delivery_fee",
        "status",
        "print_status",
        "expected_time_minutes",
        "created_at",
    )
    list_filter = ("service_type", "status", "print_status")
    search_fields = ("invoice_number", "profile__full_name", "address_snapshot")
    inlines = [CustomerOrderItemInline]
