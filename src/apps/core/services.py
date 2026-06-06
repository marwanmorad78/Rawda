import json
import logging
from urllib import error, request

from django.conf import settings
from django.utils import timezone

from apps.core.models import CenterStatus, CustomerOrder
from apps.core.localization import format_quantity


logger = logging.getLogger(__name__)


def format_invoice_text(order):
    lines = [
        "Al Rawda Center",
        f"Invoice: {order.invoice_number}",
        f"Created: {timezone.localtime(order.created_at):%Y-%m-%d %H:%M}",
        f"Customer: {order.profile.full_name}",
        f"Phone: {order.profile.phone_number}",
        f"Service: {order.get_service_type_display()}",
    ]
    if order.address_snapshot:
        lines.append(f"Address: {order.address_snapshot}")
    lines.extend(["", "Items:"])
    for item in order.items.all():
        quantity = format_quantity(item.quantity, item.is_weight_based, "en")
        lines.append(f"- {item.title} x {quantity}: {item.line_total_min:g}")
    lines.extend(
        [
            "",
            f"Subtotal: {order.subtotal_min:g}",
            f"Delivery: {order.delivery_fee:g}",
            f"Total: {order.total_min:g}",
            "",
            "Thank you.",
        ]
    )
    return "\n".join(lines)


def build_invoice_payload(order):
    order = (
        CustomerOrder.objects.select_related("profile", "address")
        .prefetch_related("items")
        .get(pk=order.pk)
    )
    return {
        "invoice_number": order.invoice_number,
        "created_at": order.created_at.isoformat(),
        "accepted_at": order.accepted_at.isoformat() if order.accepted_at else None,
        "customer": {
            "name": order.profile.full_name,
            "phone": order.profile.phone_number,
        },
        "service_type": order.service_type,
        "address": order.address_snapshot,
        "subtotal": str(order.subtotal_min),
        "delivery_fee": str(order.delivery_fee),
        "total": str(order.total_min),
        "items": [
            {
                "title": item.title,
                "category": item.category_label,
                "quantity": str(item.quantity),
                "display_quantity": format_quantity(item.quantity, item.is_weight_based, "en"),
                "is_weight_based": item.is_weight_based,
                "unit_price": str(item.unit_price),
                "line_total": str(item.line_total_min),
            }
            for item in order.items.all()
        ],
        "invoice_text": format_invoice_text(order),
    }


def send_order_to_print_service(order):
    if not getattr(settings, "INVOICE_PRINT_ENABLED", False):
        return False, "Invoice print service is disabled."

    endpoint = getattr(settings, "INVOICE_PRINT_SERVICE_URL", "")
    token = getattr(settings, "INVOICE_PRINT_SERVICE_TOKEN", "")
    if not endpoint or not token:
        return False, "Invoice print service URL or token is not configured."

    payload = json.dumps(build_invoice_payload(order)).encode("utf-8")
    print_request = request.Request(
        endpoint,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Print-Token": token,
        },
    )
    timeout = getattr(settings, "INVOICE_PRINT_TIMEOUT_SECONDS", 3)
    try:
        with request.urlopen(print_request, timeout=timeout) as response:
            if 200 <= response.status < 300:
                logger.info("Invoice print sent for order %s.", order.invoice_number)
                return True, ""
            return False, f"Print service returned HTTP {response.status}."
    except (error.URLError, TimeoutError, OSError) as exc:
        logger.warning("Invoice print failed for order %s: %s", order.invoice_number, exc)
        return False, str(exc)


def record_print_attempt(order):
    if not getattr(settings, "INVOICE_PRINT_ENABLED", False):
        return False

    success, message = send_order_to_print_service(order)
    order.print_attempted_at = timezone.now()
    order.print_status = CustomerOrder.PRINT_PRINTED if success else CustomerOrder.PRINT_FAILED
    order.print_error = "" if success else message[:2000]
    order.save(update_fields=["print_status", "print_attempted_at", "print_error", "updated_at"])
    return success


def mark_order_accepted(order, expected_time_minutes=None, print_invoice=False):
    update_fields = ["status", "accepted_at", "updated_at"]
    order.status = CustomerOrder.STATUS_BEING_PREPARED
    order.accepted_at = timezone.now()
    if expected_time_minutes is not None:
        order.expected_time_minutes = expected_time_minutes
        update_fields.append("expected_time_minutes")
    order.save(update_fields=update_fields)
    if print_invoice:
        record_print_attempt(order)
    return order


def move_accepted_orders_to_preparing():
    updated_count = CustomerOrder.objects.filter(status=CustomerOrder.STATUS_ACCEPTED).update(
        status=CustomerOrder.STATUS_BEING_PREPARED,
        updated_at=timezone.now(),
    )
    return updated_count


def sync_center_status_and_auto_accept_waiting_orders(print_invoices=False):
    moved_count = move_accepted_orders_to_preparing()
    center_status = CenterStatus.get_current().refresh_availability()
    if not center_status.is_available():
        return moved_count

    accepted_count = 0
    waiting_orders = (
        CustomerOrder.objects.select_related("profile")
        .filter(status=CustomerOrder.STATUS_WAITING_BUSY_CENTER)
        .order_by("created_at", "id")
    )
    for order in waiting_orders:
        mark_order_accepted(order, print_invoice=print_invoices)
        accepted_count += 1
    return moved_count + accepted_count
