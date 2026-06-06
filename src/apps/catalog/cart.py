from decimal import Decimal, InvalidOperation

from apps.catalog.models import Product, ProductCompanyOption, ProductOption
from apps.core.localization import (
    format_price_range,
    format_quantity,
    format_syp,
    get_language,
    localize_instance,
)
from apps.core.pricing import (
    get_active_site_settings,
    get_effective_product_company_option_price,
    get_effective_product_option_price,
    get_effective_product_price,
    get_effective_promotion_price,
    product_is_sold_by_weight,
    round_money,
    round_to_nearest_ten,
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
PRODUCT_OPTION_ITEM_TYPE = "product-option"
PRODUCT_COMPANY_OPTION_ITEM_TYPE = "product-company-option"
PROMOTION_ITEM_TYPE = "promotion"
SERVICE_PICKUP = "pickup"
SERVICE_DELIVERY = "delivery"
SERVICE_TYPES = {SERVICE_PICKUP, SERVICE_DELIVERY}
WEIGHT_MIN_KG = Decimal("0.5")
WEIGHT_MAX_KG = Decimal("10")
WEIGHT_STEP_KG = Decimal("0.5")
WEIGHT_ESTIMATE_INCREMENT_KG = Decimal("0.1")


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


def parse_decimal_quantity(value, default=Decimal("0")):
    try:
        quantity = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)
    return quantity if quantity.is_finite() else Decimal(default)


def serialize_quantity(value):
    return format(Decimal(value).normalize(), "f")


def validate_quantity(quantity, is_weight_based=False, allow_zero=False):
    quantity = parse_decimal_quantity(quantity)
    if allow_zero and quantity == 0:
        return quantity
    if is_weight_based:
        if (
            quantity < WEIGHT_MIN_KG
            or quantity > WEIGHT_MAX_KG
            or quantity % WEIGHT_STEP_KG != 0
        ):
            raise ValueError("Invalid weight quantity.")
        return quantity
    if quantity < 1 or quantity != quantity.to_integral_value():
        raise ValueError("Invalid item quantity.")
    return quantity


def normalize_cart_entry(entry):
    if isinstance(entry, dict):
        return {
            "quantity": max(parse_decimal_quantity(entry.get("quantity")), Decimal("0")),
            "note": str(entry.get("note") or "").strip(),
        }
    return {"quantity": max(parse_decimal_quantity(entry), Decimal("0")), "note": ""}


def get_item_note(request, item_type, item_id):
    cart = get_cart_data(request)
    return normalize_cart_entry(cart.get(make_item_key(item_type, item_id), 0))["note"]


def add_item(request, item_type, item_id, quantity=1, note="", is_weight_based=False):
    cart = get_cart_data(request)
    key = make_item_key(item_type, item_id)
    entry = normalize_cart_entry(cart.get(key, 0))
    quantity = validate_quantity(quantity, is_weight_based=is_weight_based)
    entry["quantity"] = validate_quantity(
        entry["quantity"] + quantity,
        is_weight_based=is_weight_based,
    )
    clean_note = str(note or "").strip()
    if clean_note:
        entry["note"] = clean_note[:500]
    entry["quantity"] = serialize_quantity(entry["quantity"])
    cart[key] = entry
    save_cart_data(request, cart)


def update_item(request, item_type, item_id, quantity, is_weight_based=False):
    cart = get_cart_data(request)
    key = make_item_key(item_type, item_id)
    quantity = validate_quantity(
        quantity,
        is_weight_based=is_weight_based,
        allow_zero=not is_weight_based,
    )
    if quantity <= 0:
        cart.pop(key, None)
    else:
        entry = normalize_cart_entry(cart.get(key, 0))
        entry["quantity"] = serialize_quantity(quantity)
        cart[key] = entry
    save_cart_data(request, cart)


def update_item_note(request, item_type, item_id, note):
    cart = get_cart_data(request)
    key = make_item_key(item_type, item_id)
    if key not in cart:
        return False
    entry = normalize_cart_entry(cart.get(key, 0))
    if entry["quantity"] <= 0:
        cart.pop(key, None)
    else:
        entry["quantity"] = serialize_quantity(entry["quantity"])
        entry["note"] = str(note or "").strip()[:500]
        cart[key] = entry
    save_cart_data(request, cart)
    return True


def remove_item(request, item_type, item_id):
    cart = get_cart_data(request)
    key = make_item_key(item_type, item_id)
    cart.pop(key, None)
    save_cart_data(request, cart)


def add_product(request, product_id, quantity=1, note="", is_weight_based=False):
    add_item(request, PRODUCT_ITEM_TYPE, product_id, quantity, note, is_weight_based)


def add_product_option(request, option_id, quantity=1, note="", is_weight_based=False):
    add_item(request, PRODUCT_OPTION_ITEM_TYPE, option_id, quantity, note, is_weight_based)


def add_product_company_option(request, option_id, quantity=1, note="", is_weight_based=False):
    add_item(
        request,
        PRODUCT_COMPANY_OPTION_ITEM_TYPE,
        option_id,
        quantity,
        note,
        is_weight_based,
    )


def add_promotion(request, promotion_id, quantity=1):
    add_item(request, PROMOTION_ITEM_TYPE, promotion_id, quantity)


def build_cart(request):
    language = get_language(request)
    site_settings = get_active_site_settings()
    cart = get_cart_data(request)
    parsed_items = [
        (parse_item_key(key), normalize_cart_entry(entry))
        for key, entry in cart.items()
    ]
    product_ids = [item_id for (item_type, item_id), _ in parsed_items if item_type == PRODUCT_ITEM_TYPE]
    option_ids = [
        item_id for (item_type, item_id), _ in parsed_items if item_type == PRODUCT_OPTION_ITEM_TYPE
    ]
    company_option_ids = [
        item_id
        for (item_type, item_id), _ in parsed_items
        if item_type == PRODUCT_COMPANY_OPTION_ITEM_TYPE
    ]
    promotion_ids = [item_id for (item_type, item_id), _ in parsed_items if item_type == PROMOTION_ITEM_TYPE]

    products = Product.objects.filter(id__in=product_ids, category__is_active=True).select_related(
        "category",
        "category__parent",
    )
    options = ProductOption.objects.filter(
        id__in=option_ids,
        product__product_type=Product.PRODUCT_TYPE_NORMAL,
        product__category__is_active=True,
    ).select_related("product", "product__category", "product__category__parent")
    company_options = ProductCompanyOption.objects.filter(
        id__in=company_option_ids,
        company__product__product_type=Product.PRODUCT_TYPE_COMPANY_GROUPED,
        company__product__category__is_active=True,
    ).select_related(
        "company",
        "company__product",
        "company__product__category",
        "company__product__category__parent",
    )
    promotions = Promotion.objects.filter(id__in=promotion_ids)
    products_by_id = {product.id: product for product in products}
    options_by_id = {option.id: option for option in options}
    company_options_by_id = {option.id: option for option in company_options}
    promotions_by_id = {promotion.id: promotion for promotion in promotions}
    items = []
    subtotal = Decimal("0")
    subtotal_max = Decimal("0")

    for (item_type, item_id), entry in parsed_items:
        quantity = entry["quantity"]
        note = entry["note"]
        if quantity <= 0:
            continue
        if item_type == PRODUCT_ITEM_TYPE:
            product = products_by_id.get(item_id)
            if not product:
                continue
            if product.has_options or product.is_company_grouped:
                continue
            is_weight_based = product_is_sold_by_weight(product)
            try:
                quantity = validate_quantity(quantity, is_weight_based=is_weight_based)
            except ValueError:
                continue
            localize_instance(product.category, language, ["name", "description"])
            localize_instance(product, language, ["name", "short_description", "description", "unit_label"])
            effective_price = get_effective_product_price(product, site_settings)
            line_total = round_money(effective_price * quantity)
            line_total_max = (
                round_money(effective_price * (quantity + WEIGHT_ESTIMATE_INCREMENT_KG))
                if is_weight_based
                else line_total
            )
            subtotal += line_total
            subtotal_max += line_total_max
            items.append(
                {
                    "item_type": PRODUCT_ITEM_TYPE,
                    "item_id": product.id,
                    "cart_key": make_item_key(PRODUCT_ITEM_TYPE, product.id),
                    "product_id": product.id,
                    "title": product.display_name,
                    "subtitle": product.display_short_description,
                    "category_label": product.category.display_name,
                    "quantity": quantity,
                    "display_quantity": format_quantity(quantity, is_weight_based, language),
                    "note": note,
                    "unit_label": product.display_unit_label,
                    "image_url": product.primary_image.url if product.primary_image else product.external_image_url,
                    "unit_price": effective_price,
                    "line_total": line_total,
                    "line_total_min": line_total,
                    "line_total_max": line_total_max,
                    "is_weight_based": is_weight_based,
                    "is_unavailable": not product.is_available,
                    "unavailable_message": "هذا الصنف لم يعد متوفراً" if language == "ar" else "This item is no longer available.",
                    "display_unit_price": format_syp(effective_price, language),
                    "display_line_total": format_syp(line_total, language),
                    "display_line_total_range": format_price_range(line_total, line_total_max, language),
                }
            )
            continue

        if item_type == PRODUCT_OPTION_ITEM_TYPE:
            option = options_by_id.get(item_id)
            if not option:
                continue
            product = option.product
            is_weight_based = product_is_sold_by_weight(product)
            try:
                quantity = validate_quantity(quantity, is_weight_based=is_weight_based)
            except ValueError:
                continue
            localize_instance(product.category, language, ["name", "description"])
            localize_instance(product, language, ["name", "short_description", "description", "unit_label"])
            effective_price = get_effective_product_option_price(option, site_settings)
            line_total = round_money(effective_price * quantity)
            line_total_max = (
                round_money(effective_price * (quantity + WEIGHT_ESTIMATE_INCREMENT_KG))
                if is_weight_based
                else line_total
            )
            subtotal += line_total
            subtotal_max += line_total_max
            title = f"{product.display_name} - {option.name}"
            items.append(
                {
                    "item_type": PRODUCT_OPTION_ITEM_TYPE,
                    "item_id": option.id,
                    "cart_key": make_item_key(PRODUCT_OPTION_ITEM_TYPE, option.id),
                    "product_id": product.id,
                    "title": title,
                    "subtitle": product.display_short_description,
                    "category_label": product.category.display_name,
                    "option_label": option.name,
                    "quantity": quantity,
                    "display_quantity": format_quantity(quantity, is_weight_based, language),
                    "note": note,
                    "unit_label": product.display_unit_label,
                    "image_url": product.primary_image.url if product.primary_image else product.external_image_url,
                    "unit_price": effective_price,
                    "line_total": line_total,
                    "line_total_min": line_total,
                    "line_total_max": line_total_max,
                    "is_weight_based": is_weight_based,
                    "is_unavailable": (not product.is_available) or (not option.is_available),
                    "unavailable_message": "هذا الصنف لم يعد متوفراً" if language == "ar" else "This item is no longer available.",
                    "display_unit_price": format_syp(effective_price, language),
                    "display_line_total": format_syp(line_total, language),
                    "display_line_total_range": format_price_range(line_total, line_total_max, language),
                }
            )
            continue

        if item_type == PRODUCT_COMPANY_OPTION_ITEM_TYPE:
            option = company_options_by_id.get(item_id)
            if not option:
                continue
            company = option.company
            product = company.product
            is_weight_based = product_is_sold_by_weight(product)
            try:
                quantity = validate_quantity(quantity, is_weight_based=is_weight_based)
            except ValueError:
                continue
            localize_instance(product.category, language, ["name", "description"])
            localize_instance(product, language, ["name", "short_description", "description", "unit_label"])
            effective_price = get_effective_product_company_option_price(option, site_settings)
            line_total = round_money(effective_price * quantity)
            line_total_max = (
                round_money(effective_price * (quantity + WEIGHT_ESTIMATE_INCREMENT_KG))
                if is_weight_based
                else line_total
            )
            subtotal += line_total
            subtotal_max += line_total_max
            items.append(
                {
                    "item_type": PRODUCT_COMPANY_OPTION_ITEM_TYPE,
                    "item_id": option.id,
                    "cart_key": make_item_key(PRODUCT_COMPANY_OPTION_ITEM_TYPE, option.id),
                    "product_id": product.id,
                    "company_id": company.id,
                    "selected_option_id": option.id,
                    "title": product.display_name,
                    "subtitle": product.display_short_description,
                    "category_label": product.category.display_name,
                    "company_label": company.name,
                    "option_label": option.name,
                    "quantity": quantity,
                    "display_quantity": format_quantity(quantity, is_weight_based, language),
                    "note": note,
                    "unit_label": product.display_unit_label,
                    "image_url": product.primary_image.url if product.primary_image else product.external_image_url,
                    "unit_price": effective_price,
                    "line_total": line_total,
                    "line_total_min": line_total,
                    "line_total_max": line_total_max,
                    "is_weight_based": is_weight_based,
                    "is_unavailable": (
                        (not product.is_available)
                        or (not company.is_active)
                        or (not option.is_available)
                    ),
                    "unavailable_message": "هذا الصنف لم يعد متوفراً" if language == "ar" else "This item is no longer available.",
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
            try:
                quantity = validate_quantity(quantity)
            except ValueError:
                continue
            localize_instance(promotion, language, ["title", "subtitle", "description", "badge_text", "cta_text"])
            effective_price = get_effective_promotion_price(promotion, site_settings)
            line_total = round_money(effective_price * quantity)
            subtotal += line_total
            subtotal_max += line_total
            items.append(
                {
                    "item_type": PROMOTION_ITEM_TYPE,
                    "item_id": promotion.id,
                    "cart_key": make_item_key(PROMOTION_ITEM_TYPE, promotion.id),
                    "title": promotion.display_title,
                    "subtitle": promotion.display_description or promotion.display_subtitle,
                    "category_label": "عرض" if language == "ar" else "Offer",
                    "quantity": quantity,
                    "display_quantity": format_quantity(quantity, False, language),
                    "note": note,
                    "unit_label": "",
                    "image_url": promotion.image.url if promotion.image else promotion.external_image_url,
                    "unit_price": effective_price,
                    "line_total": line_total,
                    "line_total_min": line_total,
                    "line_total_max": line_total,
                    "is_weight_based": False,
                    "is_unavailable": False,
                    "unavailable_message": "",
                    "display_unit_price": format_syp(effective_price, language),
                    "display_line_total": format_syp(line_total, language),
                    "display_line_total_range": format_syp(line_total, language),
                }
            )

    subtotal = round_to_nearest_ten(subtotal)
    subtotal_max = round_to_nearest_ten(subtotal_max)

    return {
        "items": items,
        "count": len(items),
        "subtotal": subtotal,
        "subtotal_min": subtotal,
        "subtotal_max": subtotal_max,
        "has_weight_items": any(item["is_weight_based"] for item in items),
        "has_unavailable_items": any(item.get("is_unavailable") for item in items),
        "display_subtotal": format_syp(subtotal, language),
        "display_subtotal_range": format_price_range(subtotal, subtotal_max, language),
    }
