from decimal import Decimal

from apps.catalog.models import Product
from apps.core.localization import format_price_range, format_syp, get_language, localize_instance
from apps.core.pricing import (
    get_active_site_settings,
    get_effective_product_price,
    get_effective_promotion_price,
    product_is_sold_by_weight,
)
from apps.promotions.models import Promotion


CART_SESSION_KEY = "catalog_cart"
CHECKOUT_ADDRESS_SESSION_KEY = "catalog_checkout_address"
CHECKOUT_SERVICE_SESSION_KEY = "catalog_checkout_service"
CART_SKIP_RELOAD_CLEAR_SESSION_KEY = "catalog_skip_reload_clear"
CART_RELATED_SESSION_KEYS = {
    CART_SESSION_KEY,
    CHECKOUT_ADDRESS_SESSION_KEY,
    CHECKOUT_SERVICE_SESSION_KEY,
}
PRODUCT_ITEM_TYPE = "product"
PROMOTION_ITEM_TYPE = "promotion"
SERVICE_PICKUP = "pickup"
SERVICE_DELIVERY = "delivery"
SERVICE_TYPES = {SERVICE_PICKUP, SERVICE_DELIVERY}
WEIGHT_RANGE_FACTOR = Decimal("1.25")


def get_cart_data(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def save_cart_data(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def set_checkout_address(request, address_id):
    request.session[CHECKOUT_ADDRESS_SESSION_KEY] = address_id
    request.session.modified = True


def get_checkout_address_id(request):
    return request.session.get(CHECKOUT_ADDRESS_SESSION_KEY)


def set_checkout_service_type(request, service_type):
    request.session[CHECKOUT_SERVICE_SESSION_KEY] = (
        service_type if service_type in SERVICE_TYPES else SERVICE_PICKUP
    )
    request.session.modified = True


def get_checkout_service_type(request):
    service_type = request.session.get(CHECKOUT_SERVICE_SESSION_KEY)
    return service_type if service_type in SERVICE_TYPES else SERVICE_PICKUP


def clear_checkout_address(request):
    if CHECKOUT_ADDRESS_SESSION_KEY in request.session:
        request.session.pop(CHECKOUT_ADDRESS_SESSION_KEY, None)
        request.session.modified = True


def clear_cart(request):
    request.session.pop(CART_SESSION_KEY, None)
    clear_checkout_address(request)
    request.session.pop(CHECKOUT_SERVICE_SESSION_KEY, None)
    request.session.pop(CART_SKIP_RELOAD_CLEAR_SESSION_KEY, None)
    request.session.modified = True


def preserve_cart_for_next_request(request):
    request.session[CART_SKIP_RELOAD_CLEAR_SESSION_KEY] = True
    request.session.modified = True


def make_item_key(item_type, item_id):
    return f"{item_type}:{item_id}"


def parse_item_key(key):
    item_type, _, raw_item_id = str(key).partition(":")
    if not item_type or not raw_item_id:
        item_type = PRODUCT_ITEM_TYPE
        raw_item_id = key
    return item_type, int(raw_item_id)


def add_item(request, item_type, item_id, quantity=1):
    cart = get_cart_data(request)
    key = make_item_key(item_type, item_id)
    cart[key] = cart.get(key, 0) + quantity
    save_cart_data(request, cart)


def update_item(request, item_type, item_id, quantity):
    cart = get_cart_data(request)
    key = make_item_key(item_type, item_id)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity
    save_cart_data(request, cart)


def remove_item(request, item_type, item_id):
    cart = get_cart_data(request)
    key = make_item_key(item_type, item_id)
    quantity = cart.get(key, 0)
    if quantity <= 1:
        cart.pop(key, None)
    else:
        cart[key] = quantity - 1
    save_cart_data(request, cart)


def add_product(request, product_id, quantity=1):
    add_item(request, PRODUCT_ITEM_TYPE, product_id, quantity)


def add_promotion(request, promotion_id, quantity=1):
    add_item(request, PROMOTION_ITEM_TYPE, promotion_id, quantity)


def build_cart(request):
    language = get_language(request)
    site_settings = get_active_site_settings()
    cart = get_cart_data(request)
    parsed_items = [(parse_item_key(key), quantity) for key, quantity in cart.items()]
    product_ids = [item_id for (item_type, item_id), _ in parsed_items if item_type == PRODUCT_ITEM_TYPE]
    promotion_ids = [item_id for (item_type, item_id), _ in parsed_items if item_type == PROMOTION_ITEM_TYPE]

    products = Product.objects.filter(id__in=product_ids, is_available=True).select_related("category")
    promotions = Promotion.objects.filter(id__in=promotion_ids)
    products_by_id = {product.id: product for product in products}
    promotions_by_id = {promotion.id: promotion for promotion in promotions}
    items = []
    subtotal = Decimal("0")
    subtotal_max = Decimal("0")

    for (item_type, item_id), quantity in parsed_items:
        if item_type == PRODUCT_ITEM_TYPE:
            product = products_by_id.get(item_id)
            if not product:
                continue
            localize_instance(product.category, language, ["name", "description"])
            localize_instance(product, language, ["name", "short_description", "description", "unit_label"])
            effective_price = get_effective_product_price(product, site_settings)
            line_total = effective_price * quantity
            is_weight_based = product_is_sold_by_weight(product)
            line_total_max = line_total * WEIGHT_RANGE_FACTOR if is_weight_based else line_total
            subtotal += line_total
            subtotal_max += line_total_max
            items.append(
                {
                    "item_type": PRODUCT_ITEM_TYPE,
                    "item_id": product.id,
                    "title": product.display_name,
                    "subtitle": product.display_short_description,
                    "category_label": product.category.display_name,
                    "quantity": quantity,
                    "unit_label": product.display_unit_label,
                    "unit_price": effective_price,
                    "line_total": line_total,
                    "line_total_min": line_total,
                    "line_total_max": line_total_max,
                    "is_weight_based": is_weight_based,
                    "display_unit_price": format_syp(effective_price, language),
                    "display_line_total": format_syp(line_total, language),
                    "display_line_total_range": format_price_range(line_total, line_total_max, language),
                }
            )
            continue

        if item_type == PROMOTION_ITEM_TYPE:
            promotion = promotions_by_id.get(item_id)
            if not promotion:
                continue
            localize_instance(promotion, language, ["title", "subtitle", "description", "badge_text", "cta_text"])
            effective_price = get_effective_promotion_price(promotion, site_settings)
            line_total = effective_price * quantity
            subtotal += line_total
            subtotal_max += line_total
            items.append(
                {
                    "item_type": PROMOTION_ITEM_TYPE,
                    "item_id": promotion.id,
                    "title": promotion.display_title,
                    "subtitle": promotion.display_description or promotion.display_subtitle,
                    "category_label": "عرض" if language == "ar" else "Offer",
                    "quantity": quantity,
                    "unit_label": "",
                    "unit_price": effective_price,
                    "line_total": line_total,
                    "line_total_min": line_total,
                    "line_total_max": line_total,
                    "is_weight_based": False,
                    "display_unit_price": format_syp(effective_price, language),
                    "display_line_total": format_syp(line_total, language),
                    "display_line_total_range": format_syp(line_total, language),
                }
            )

    return {
        "items": items,
        "count": len(items),
        "subtotal": subtotal,
        "subtotal_min": subtotal,
        "subtotal_max": subtotal_max,
        "has_weight_items": any(item["is_weight_based"] for item in items),
        "display_subtotal": format_syp(subtotal, language),
        "display_subtotal_range": format_price_range(subtotal, subtotal_max, language),
    }
