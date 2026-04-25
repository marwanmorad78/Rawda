from django.contrib import admin

from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    fields = ("description", "price", "is_price_linked_to_dollar", "image", "is_active", "display_order")
    list_display = ("title", "price", "is_price_linked_to_dollar", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    search_fields = ("title", "description")
