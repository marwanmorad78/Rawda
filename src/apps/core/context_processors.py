from apps.catalog.cart import build_cart
from apps.catalog.models import Category
from apps.core.models import SiteSettings
from apps.core.localization import get_language, get_ui_strings, localize_instance, localize_queryset, with_lang_query


def global_site_context(request):
    current_language = get_language(request)
    site_settings = SiteSettings.objects.filter(is_active=True).first()
    localize_instance(
        site_settings,
        current_language,
        [
            "store_name",
            "tagline",
            "about_text",
            "address",
            "working_hours_summary",
            "hero_title",
            "hero_subtitle",
            "hero_cta_text",
        ],
    )
    categories = localize_queryset(
        Category.objects.filter(is_active=True).order_by("display_order", "name"),
        current_language,
        ["name", "description"],
    )
    cart_summary = build_cart(request)
    return {
        "site_settings": site_settings,
        "nav_categories": categories,
        "current_language": current_language,
        "ui": get_ui_strings(current_language),
        "is_rtl": current_language == "ar",
        "switch_to_ar_url": with_lang_query("/language/", "ar"),
        "switch_to_en_url": with_lang_query("/language/", "en"),
        "cart_count": cart_summary["count"],
        "cart_subtotal": cart_summary["display_subtotal"],
    }
