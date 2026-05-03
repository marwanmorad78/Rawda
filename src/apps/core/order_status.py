from apps.core.localization import format_price_range, format_syp
from apps.core.models import CustomerOrder


STATUS_LABEL_KEYS = {
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


def attach_order_display(order, labels, language):
    order.display_total = format_price_range(order.total_min, order.total_max, language)
    order.display_delivery_fee = format_syp(order.delivery_fee, language)
    order.display_status_label = get_status_label(labels, order.status)
    order.status_steps = build_order_status_steps(order, labels)
    order.next_status = order.get_next_status()
    order.next_status_label = get_status_label(labels, order.next_status) if order.next_status else ""
    if order.expected_time_minutes:
        order.display_expected_time = labels["expected_time_minutes"].format(minutes=order.expected_time_minutes)
    else:
        order.display_expected_time = labels["waiting_manager_confirmation"]
    for item in order.items.all():
        item.display_line_total = format_price_range(item.line_total_min, item.line_total_max, language)
        item.display_unit_price = format_syp(item.unit_price, language)
    return order


def attach_orders_display(orders, labels, language):
    for order in orders:
        attach_order_display(order, labels, language)
    return orders


def suggested_expected_minutes():
    active_count = CustomerOrder.objects.filter(status__in=CustomerOrder.ACTIVE_STATUSES).count()
    return 20 + max(active_count - 1, 0) * 5
