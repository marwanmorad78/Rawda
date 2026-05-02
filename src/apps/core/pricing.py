from decimal import Decimal

from apps.core.localization import format_syp
from apps.core.models import SiteSettings


def get_active_site_settings():
    return SiteSettings.objects.filter(is_active=True).first()


def get_dollar_price(site_settings=None):
    source = site_settings if site_settings is not None else get_active_site_settings()
    return getattr(source, "dollar_price", Decimal("0")) or Decimal("0")


def product_uses_dollar_price(product):
    if getattr(product, "price_link_mode", "custom") == "inherit":
        return bool(getattr(product.category, "is_price_linked_to_dollar", False))
    return bool(getattr(product, "is_price_linked_to_dollar", False))


def product_is_sold_by_weight(product):
    if getattr(product, "sold_by_weight_mode", "custom") == "inherit":
        return bool(getattr(product.category, "sold_by_weight", False))
    return bool(getattr(product, "sold_by_weight", False))


def get_effective_product_price(product, site_settings=None):
    base_price = getattr(product, "price", Decimal("0")) or Decimal("0")
    if product_uses_dollar_price(product):
        return base_price * get_dollar_price(site_settings)
    return base_price


def get_effective_product_option_price(option, site_settings=None):
    base_price = getattr(option, "price", Decimal("0")) or Decimal("0")
    if product_uses_dollar_price(option.product):
        return base_price * get_dollar_price(site_settings)
    return base_price


def set_product_display_price(product, language, site_settings=None):
    option_prices = []
    if getattr(product, "has_options", False):
        options = getattr(product, "prefetched_options", None)
        if options is None:
            options = list(product.options.all())
        for option in options:
            option.effective_price = get_effective_product_option_price(option, site_settings)
            option.display_price = format_syp(option.effective_price, language)
            option_prices.append(option.effective_price)
    effective_price = min(option_prices) if option_prices else get_effective_product_price(product, site_settings)
    product.effective_price = effective_price
    product.effective_is_price_linked_to_dollar = product_uses_dollar_price(product)
    product.effective_sold_by_weight = product_is_sold_by_weight(product)
    product.display_price = format_syp(effective_price, language)
    product.display_price_is_starting_from = bool(option_prices)
    return product


def get_effective_promotion_price(promotion, site_settings=None):
    base_price = getattr(promotion, "price", Decimal("0")) or Decimal("0")
    if getattr(promotion, "is_price_linked_to_dollar", False):
        return base_price * get_dollar_price(site_settings)
    return base_price


def set_promotion_display_price(promotion, language, site_settings=None):
    effective_price = get_effective_promotion_price(promotion, site_settings)
    promotion.effective_price = effective_price
    promotion.display_price = format_syp(effective_price, language)
    return promotion
