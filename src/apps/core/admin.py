from django.contrib import admin

from .models import CustomerAddress, CustomerOrder, DeliveryArea, DeliverySubArea, SiteSettings


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


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("profile", "area", "sub_area", "street_address", "is_default", "updated_at")
    list_filter = ("area", "sub_area", "is_default")
    search_fields = ("profile__full_name", "street_address", "building", "nearby_landmark")


@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "profile", "service_type", "delivery_fee", "status", "expected_time_minutes", "created_at")
    list_filter = ("service_type", "status")
    search_fields = ("invoice_number", "profile__full_name", "address_snapshot")
