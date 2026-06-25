from decimal import Decimal, ROUND_HALF_UP

from apps.core.localization import format_syp
from apps.core.models import SiteSettings


def get_active_site_settings():
    return SiteSettings.objects.filter(is_active=True).first()


def round_money(value):
    return Decimal(value or 0).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def round_to_nearest_ten(value):
    amount = Decimal(value or 0)
    return (amount / Decimal("10")).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * Decimal("10")


def get_dollar_price(site_settings=None):
    source = site_settings if site_settings is not None else get_active_site_settings()
    return round_money(getattr(source, "dollar_price", Decimal("0")) or Decimal("0"))


def product_uses_dollar_price(product):
    if getattr(product, "price_link_mode", "custom") == "inherit":
        category = getattr(product, "category", None)
        if category is not None and hasattr(category, "effective_is_price_linked_to_dollar"):
            return bool(category.effective_is_price_linked_to_dollar)
        return bool(getattr(category, "is_price_linked_to_dollar", False))
    return bool(getattr(product, "is_price_linked_to_dollar", False))


def product_is_sold_by_weight(product):
    if getattr(product, "sold_by_weight_mode", "custom") == "inherit":
        category = getattr(product, "category", None)
        if category is not None and hasattr(category, "effective_sold_by_weight"):
            return bool(category.effective_sold_by_weight)
        return bool(getattr(category, "sold_by_weight", False))
    return bool(getattr(product, "sold_by_weight", False))


def get_effective_product_price(product, site_settings=None):
    base_price = getattr(product, "price", Decimal("0")) or Decimal("0")
    if product_uses_dollar_price(product):
        return round_money(base_price * get_dollar_price(site_settings))
    return round_money(base_price)


def get_effective_product_option_price(option, site_settings=None):
    base_price = getattr(option, "price", Decimal("0")) or Decimal("0")
    if product_uses_dollar_price(option.product):
        return round_money(base_price * get_dollar_price(site_settings))
    return round_money(base_price)


def get_effective_product_company_option_price(option, site_settings=None):
    base_price = getattr(option, "price", Decimal("0")) or Decimal("0")
    company = option.company
    company_uses_dollar = getattr(company, "is_price_linked_to_dollar", None)
    if company_uses_dollar is None:
        company_uses_dollar = product_uses_dollar_price(company.product)
    if company_uses_dollar:
        return round_money(base_price * get_dollar_price(site_settings))
    return round_money(base_price)


def set_product_display_price(product, language, site_settings=None):
    option_prices = []
    is_weight_based = product_is_sold_by_weight(product)
    display_factor = Decimal("0.5") if is_weight_based else Decimal("1")
    if getattr(product, "is_company_grouped", False):
        companies = getattr(product, "prefetched_companies", None)
        if companies is None:
            companies = list(
                product.companies.filter(company__is_active=True)
                .select_related("company")
                .prefetch_related("options")
            )
        for company in companies:
            company_options = getattr(company, "prefetched_options", None)
            if company_options is None:
                company_options = list(company.options.all())
            for option in company_options:
                option.effective_price = get_effective_product_company_option_price(option, site_settings)
                option.display_price = format_syp(
                    round_money(option.effective_price * display_factor),
                    language,
                )
                option_prices.append(option.effective_price)
    elif getattr(product, "has_options", False):
        options = getattr(product, "prefetched_options", None)
        if options is None:
            options = list(product.options.all())
        for option in options:
            option.effective_price = get_effective_product_option_price(option, site_settings)
            option.display_price = format_syp(
                round_money(option.effective_price * display_factor),
                language,
            )
            option_prices.append(option.effective_price)
    effective_price = min(option_prices) if option_prices else get_effective_product_price(product, site_settings)
    product.effective_price = effective_price
    product.effective_is_price_linked_to_dollar = product_uses_dollar_price(product)
    product.effective_sold_by_weight = is_weight_based
    product.display_price = format_syp(round_money(effective_price * display_factor), language)
    product.display_price_is_starting_from = bool(option_prices)
    return product


def get_effective_promotion_price(promotion, site_settings=None):
    base_price = getattr(promotion, "price", Decimal("0")) or Decimal("0")
    if getattr(promotion, "is_price_linked_to_dollar", False):
        return round_money(base_price * get_dollar_price(site_settings))
    return round_money(base_price)


def set_promotion_display_price(promotion, language, site_settings=None):
    effective_price = get_effective_promotion_price(promotion, site_settings)
    promotion.effective_price = effective_price
    promotion.display_price = format_syp(effective_price, language)
    return promotion
