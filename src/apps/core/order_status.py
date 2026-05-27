import math

from apps.core.localization import format_price_range, format_syp
from apps.core.models import CenterStatus, CustomerOrder


STATUS_LABEL_KEYS = {
    CustomerOrder.STATUS_WAITING_BUSY_CENTER: "order_status_waiting_due_to_busy_center",
    CustomerOrder.STATUS_ACCEPTED: "order_status_accepted",
    CustomerOrder.STATUS_WAITING_ACCEPT: "order_status_waiting_accept",
    CustomerOrder.STATUS_BEING_PREPARED: "order_status_being_prepared",
    CustomerOrder.STATUS_OUT_FOR_DELIVERY: "order_status_out_for_delivery",
    CustomerOrder.STATUS_READY_TO_PICKUP: "order_status_ready_to_pickup",
    CustomerOrder.STATUS_DONE: "order_status_done",
    CustomerOrder.STATUS_CANCELLED: "order_status_cancelled",
}


def get_active_order_queryset(profile):
    return (
        profile.orders.select_related("address")
        .prefetch_related("items")
        .filter(status__in=CustomerOrder.ACTIVE_STATUSES)
        .order_by("-created_at", "-id")
    )


def get_active_customer_order(profile):
    return get_active_order_queryset(profile).first()


def get_status_label(labels, status):
    label_key = STATUS_LABEL_KEYS.get(status)
    return labels.get(label_key, status) if label_key else status


def build_order_status_steps(order, labels):
    flow = order.get_status_flow()
    if order.status == CustomerOrder.STATUS_WAITING_BUSY_CENTER:
        flow = [CustomerOrder.STATUS_WAITING_BUSY_CENTER, *flow]
    elif order.status == CustomerOrder.STATUS_WAITING_ACCEPT:
        flow = [CustomerOrder.STATUS_WAITING_ACCEPT, *flow]
    current_index = flow.index(order.status) if order.status in flow else -1
    steps = []
    for index, status in enumerate(flow):
        if current_index < 0:
            state = "inactive"
        elif index < current_index:
            state = "complete"
        elif index == current_index:
            state = "current"
        else:
            state = "inactive"
        steps.append(
            {
                "status": status,
                "label": get_status_label(labels, status),
                "state": state,
            }
        )
    return steps


def attach_order_display(order, labels, language, print_auto_accepted_order=False):
    order.auto_accept_if_center_available(print_invoice=print_auto_accepted_order)
    order.display_total = format_price_range(order.total_min, order.total_max, language)
    order.display_delivery_fee = format_syp(order.delivery_fee, language)
    order.display_status_label = get_status_label(labels, order.status)
    order.status_steps = build_order_status_steps(order, labels)
    order.next_status = order.get_next_status()
    order.next_status_label = get_status_label(labels, order.next_status) if order.next_status else ""
    if order.status == CustomerOrder.STATUS_WAITING_BUSY_CENTER:
        center_status = CenterStatus.get_current().refresh_availability()
        remaining_seconds = int(center_status.remaining_busy_time().total_seconds())
        remaining_minutes = max(math.ceil(remaining_seconds / 60), 0)
        order.busy_remaining_seconds = remaining_seconds
        order.busy_remaining_minutes = remaining_minutes
        busy_message = labels.get(
            "center_busy_order_message",
            "The center is busy. Your order will be accepted automatically after {minutes} minutes.",
        )
        order.display_expected_time = busy_message.format(minutes=remaining_minutes)
    elif order.status == CustomerOrder.STATUS_ACCEPTED:
        order.display_expected_time = labels.get("order_accepted_message", get_status_label(labels, order.status))
    elif order.expected_time_minutes:
        order.display_expected_time = labels["expected_time_minutes"].format(minutes=order.expected_time_minutes)
    else:
        order.display_expected_time = labels["waiting_manager_confirmation"]
    for item in order.items.all():
        item.display_line_total = format_price_range(item.line_total_min, item.line_total_max, language)
        item.display_unit_price = format_syp(item.unit_price, language)
    return order


def attach_orders_display(orders, labels, language, print_auto_accepted_order=False):
    for order in orders:
        attach_order_display(order, labels, language, print_auto_accepted_order=print_auto_accepted_order)
    return orders


def suggested_expected_minutes():
    active_count = CustomerOrder.objects.filter(status__in=CustomerOrder.ACTIVE_STATUSES).count()
    return 20 + max(active_count - 1, 0) * 5
