from decimal import Decimal

from django.utils import timezone

from apps.catalog.cart import build_cart
from apps.core.localization import format_price_range, format_syp, get_language
from apps.core.models import CustomerOrder, CustomerOrderItem


def build_address_snapshot(address):
    if address is None:
        return ""
    parts = [address.area.name]
    if getattr(address, "sub_area_id", None):
        parts.append(address.sub_area.name)
    parts.append(address.street_address)
    if address.building:
        parts.append(f"Building: {address.building}")
    if address.floor:
        parts.append(f"Floor: {address.floor}")
    if address.apartment:
        parts.append(f"Apartment: {address.apartment}")
    if address.nearby_landmark:
        parts.append(f"Near: {address.nearby_landmark}")
    if address.notes:
        parts.append(address.notes)
    return ", ".join(part for part in parts if part)


def get_address_delivery_fee(address):
    if address is None:
        return Decimal("0")
    if getattr(address.area, "has_sub_areas", False):
        if getattr(address, "sub_area_id", None):
            return Decimal(getattr(address.sub_area, "delivery_fee", 0) or 0)
        return Decimal("0")
    return Decimal(getattr(address.area, "delivery_fee", 0) or 0)


def get_delivery_fee(address, service_type):
    zero_fee = Decimal("0")
    if service_type != CustomerOrder.SERVICE_DELIVERY or address is None:
        return zero_fee
    return get_address_delivery_fee(address)


def build_checkout_summary(request, address=None, service_type=CustomerOrder.SERVICE_PICKUP):
    language = get_language(request)
    cart = build_cart(request)
    delivery_fee = get_delivery_fee(address, service_type)
    total_min = cart["subtotal_min"] + delivery_fee
    total_max = cart["subtotal_max"] + delivery_fee
    return {
        "cart": cart,
        "service_type": service_type,
        "is_delivery": service_type == CustomerOrder.SERVICE_DELIVERY,
        "is_pickup": service_type == CustomerOrder.SERVICE_PICKUP,
        "address": address,
        "address_snapshot": build_address_snapshot(address),
        "delivery_fee": delivery_fee,
        "display_delivery_fee": format_syp(delivery_fee, language),
        "is_free_delivery": delivery_fee == 0,
        "total_min": total_min,
        "total_max": total_max,
        "display_total": format_price_range(total_min, total_max, language),
    }


def generate_invoice_number():
    return timezone.now().strftime("AR-%Y%m%d-%H%M%S")


def create_order_from_checkout(profile, address, checkout_summary):
    base_invoice_number = generate_invoice_number()
    invoice_number = base_invoice_number
    suffix = 2
    while CustomerOrder.objects.filter(invoice_number=invoice_number).exists():
        invoice_number = f"{base_invoice_number}-{suffix}"
        suffix += 1

    order = CustomerOrder.objects.create(
        profile=profile,
        address=address,
        invoice_number=invoice_number,
        service_type=checkout_summary["service_type"],
        status=CustomerOrder.STATUS_WAITING_ACCEPT,
        address_snapshot=checkout_summary["address_snapshot"],
        subtotal_min=checkout_summary["cart"]["subtotal_min"],
        subtotal_max=checkout_summary["cart"]["subtotal_max"],
        delivery_fee=checkout_summary["delivery_fee"],
        total_min=checkout_summary["total_min"],
        total_max=checkout_summary["total_max"],
    )
    CustomerOrderItem.objects.bulk_create(
        [
            CustomerOrderItem(
                order=order,
                item_type=item["item_type"],
                cart_item_id=item["item_id"],
                title=item["title"],
                category_label=item["category_label"],
                quantity=item["quantity"],
                unit_label=item.get("unit_label", ""),
                unit_price=item["unit_price"],
                line_total_min=item["line_total_min"],
                line_total_max=item["line_total_max"],
                is_weight_based=item["is_weight_based"],
            )
            for item in checkout_summary["cart"]["items"]
        ]
    )
    return order
