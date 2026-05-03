from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, TemplateView

from apps.catalog.cart import (
    add_product,
    add_product_option,
    add_promotion,
    build_cart,
    clear_cart,
    get_checkout_address_id,
    get_checkout_service_type,
    preserve_cart_for_next_request,
    remove_item,
    set_checkout_address,
    set_checkout_service_type,
    update_item,
)
from apps.catalog.checkout import build_checkout_summary, create_order_from_checkout, get_address_delivery_fee
from apps.catalog.forms import CheckoutAddressForm
from apps.core.forms import CustomerAddressForm
from apps.core.localization import format_price_range, format_syp, get_language, get_ui_strings, localize_instance, localize_queryset
from apps.core.models import CustomerOrder, CustomerProfile
from apps.core.order_status import attach_order_display, get_active_customer_order
from apps.core.pricing import get_active_site_settings, set_product_display_price
from apps.promotions.models import Promotion

from .models import Category, Product, ProductOption


def parse_quantity(value, default=1):
    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return default


def wants_json_response(request):
    accept_header = request.headers.get("Accept", "")
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in accept_header


def get_customer_profile(user):
    defaults = {
        "full_name": user.first_name or user.username,
        "phone_number": user.username,
    }
    return CustomerProfile.objects.get_or_create(user=user, defaults=defaults)[0]


def get_checkout_addresses(request):
    profile = get_customer_profile(request.user)
    return profile, profile.addresses.select_related("area", "sub_area").all()


def get_selected_checkout_address(request, addresses):
    addresses = addresses.filter(area__is_active=True)
    selected_id = get_checkout_address_id(request)
    if selected_id:
        selected = addresses.filter(pk=selected_id).first()
        if selected is not None:
            return selected
    return addresses.filter(is_default=True).first() or addresses.first()


def attach_address_delivery_fee_display(addresses, language, cart=None):
    for address in addresses:
        delivery_fee = get_address_delivery_fee(address)
        address.is_free_delivery = delivery_fee == 0
        address.display_delivery_fee = format_syp(delivery_fee, language)
        if cart is not None:
            address.display_checkout_total = format_price_range(
                cart["subtotal_min"] + delivery_fee,
                cart["subtotal_max"] + delivery_fee,
                language,
            )
    return addresses


class CategoryDetailView(DetailView):
    model = Category
    template_name = "public/category_detail.html"
    context_object_name = "category"

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def get_object(self, queryset=None):
        category = get_object_or_404(self.get_queryset(), slug=self.kwargs["slug"])
        return localize_instance(category, get_language(self.request), ["name", "description"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language(self.request)
        site_settings = get_active_site_settings()
        products = list(self.object.products.filter(is_available=True))
        for product in products:
            product.prefetched_options = list(product.options.all())
            localize_instance(product, language, ["name", "short_description", "description", "unit_label"])
            set_product_display_price(product, language, site_settings)
        context["products"] = products
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "public/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.filter(is_available=True, category__is_active=True).select_related(
            "category"
        )

    def get_object(self, queryset=None):
        product = get_object_or_404(self.get_queryset(), slug=self.kwargs["slug"])
        language = get_language(self.request)
        site_settings = get_active_site_settings()
        localize_instance(product.category, language, ["name", "description"])
        product = localize_instance(product, language, ["name", "short_description", "description", "unit_label"])
        product.prefetched_options = list(product.options.all())
        set_product_display_price(product, language, site_settings)
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language(self.request)
        site_settings = get_active_site_settings()
        related_products = list(
            Product.objects.filter(category=self.object.category, is_available=True).exclude(pk=self.object.pk)[:4]
        )
        context["related_products"] = localize_queryset(
            related_products,
            language,
            ["name", "short_description", "description", "unit_label"],
        )
        for item in context["related_products"]:
            item.prefetched_options = list(item.options.all())
            set_product_display_price(item, language, site_settings)
        return context


class AddToCartView(LoginRequiredMixin, View):
    login_url = "core:login"

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_available=True)
        quantity = max(parse_quantity(request.POST.get("quantity", 1), default=1), 1)
        language = get_language(request)
        ui = get_ui_strings(language)
        product = localize_instance(product, language, ["name"])
        selected_option = None
        if product.has_options:
            selected_option = ProductOption.objects.filter(
                pk=request.POST.get("option_id"),
                product=product,
            ).first()
            if selected_option is None:
                message = ui.get("select_product_option", "Please select an option before adding to cart.")
                if wants_json_response(request):
                    return JsonResponse({"ok": False, "message": message}, status=400)
                messages.error(request, message)
                preserve_cart_for_next_request(request)
                return redirect(request.POST.get("next") or product.get_absolute_url())
            add_product_option(request, selected_option.id, quantity)
        else:
            add_product(request, product.id, quantity)
        item_title = product.display_name
        if selected_option is not None:
            item_title = f"{item_title} - {selected_option.name}"
        message = f"{item_title}: {ui['cart_added']}"
        if wants_json_response(request):
            cart = build_cart(request)
            return JsonResponse(
                {
                    "ok": True,
                    "message": message,
                    "item_title": item_title,
                    "cart_count": cart["count"],
                    "cart_total": cart["display_subtotal"],
                    "cart_url": request.build_absolute_uri(reverse("catalog:cart")),
                }
            )
        messages.success(request, message)
        preserve_cart_for_next_request(request)
        return redirect(request.POST.get("next") or product.get_absolute_url())


class AddOfferToCartView(LoginRequiredMixin, View):
    login_url = "core:login"

    def post(self, request, slug):
        promotion = get_object_or_404(Promotion.active(), slug=slug)
        quantity = max(parse_quantity(request.POST.get("quantity", 1), default=1), 1)
        add_promotion(request, promotion.id, quantity)
        language = get_language(request)
        ui = get_ui_strings(language)
        promotion = localize_instance(promotion, language, ["title"])
        message = f"{promotion.display_title}: {ui['cart_added']}"
        if wants_json_response(request):
            cart = build_cart(request)
            return JsonResponse(
                {
                    "ok": True,
                    "message": message,
                    "item_title": promotion.display_title,
                    "cart_count": cart["count"],
                    "cart_total": cart["display_subtotal"],
                    "cart_url": request.build_absolute_uri(reverse("catalog:cart")),
                }
            )
        messages.success(request, message)
        preserve_cart_for_next_request(request)
        return redirect(request.POST.get("next") or "core:home")


class CartDetailView(LoginRequiredMixin, TemplateView):
    template_name = "public/cart.html"
    login_url = "core:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language(self.request)
        profile = CustomerProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "full_name": self.request.user.first_name or self.request.user.username,
                "phone_number": self.request.user.username,
            },
        )[0]
        active_order = get_active_customer_order(profile)
        context["cart"] = build_cart(self.request)
        context["checkout_service_type"] = get_checkout_service_type(self.request)
        context["active_order"] = (
            attach_order_display(active_order, get_ui_strings(language), language) if active_order else None
        )
        return context


class CheckoutServiceView(LoginRequiredMixin, View):
    login_url = "core:login"

    def post(self, request):
        cart = build_cart(request)
        if not cart["items"]:
            return redirect("catalog:cart")
        service_type = request.POST.get("service_type")
        if service_type not in {CustomerOrder.SERVICE_PICKUP, CustomerOrder.SERVICE_DELIVERY}:
            service_type = CustomerOrder.SERVICE_PICKUP
        set_checkout_service_type(request, service_type)
        preserve_cart_for_next_request(request)
        if service_type == CustomerOrder.SERVICE_DELIVERY:
            return redirect("catalog:checkout-address")
        return redirect("catalog:invoice")


class CartUpdateView(LoginRequiredMixin, View):
    login_url = "core:login"

    def post(self, request, item_type, item_id):
        quantity = parse_quantity(request.POST.get("quantity", 1), default=1)
        update_item(request, item_type, item_id, quantity)
        messages.success(request, get_ui_strings(get_language(request))["cart_updated"])
        preserve_cart_for_next_request(request)
        return redirect("catalog:cart")


class CartRemoveView(LoginRequiredMixin, View):
    login_url = "core:login"

    def post(self, request, item_type, item_id):
        remove_item(request, item_type, item_id)
        messages.success(request, get_ui_strings(get_language(request))["cart_removed"])
        preserve_cart_for_next_request(request)
        return redirect("catalog:cart")


class CheckoutAddressView(LoginRequiredMixin, View):
    template_name = "public/checkout_address.html"
    login_url = "core:login"

    def get_form(self, request, addresses, data=None):
        selected_address = get_selected_checkout_address(request, addresses)
        initial = {"address": selected_address.pk} if selected_address is not None else {}
        return CheckoutAddressForm(data=data, addresses=addresses, language=get_language(request), initial=initial)

    def get_address_form(self, data=None):
        return CustomerAddressForm(data=data, language=get_language(self.request))

    def render_address_step(
        self,
        request,
        cart,
        profile,
        addresses,
        form=None,
        address_form=None,
        selected_address_id=None,
        is_address_modal_open=False,
    ):
        selected_address = get_selected_checkout_address(request, addresses)
        checkout_summary = build_checkout_summary(
            request,
            selected_address,
            CustomerOrder.SERVICE_DELIVERY,
        )
        return render(
            request,
            self.template_name,
            {
                **checkout_summary,
                "cart": cart,
                "profile": profile,
                "addresses": addresses,
                "form": form or self.get_form(request, addresses),
                "address_form": address_form or self.get_address_form(),
                "selected_address_id": selected_address_id or (selected_address.pk if selected_address is not None else None),
                "is_address_modal_open": is_address_modal_open,
            },
        )

    def get(self, request):
        cart = build_cart(request)
        if not cart["items"]:
            return redirect("catalog:cart")
        if get_checkout_service_type(request) != CustomerOrder.SERVICE_DELIVERY:
            return redirect("catalog:invoice")
        profile, addresses = get_checkout_addresses(request)
        addresses = addresses.filter(area__is_active=True)
        addresses = attach_address_delivery_fee_display(addresses, get_language(request), cart)
        return self.render_address_step(request, cart, profile, addresses)

    def post(self, request):
        cart = build_cart(request)
        if not cart["items"]:
            return redirect("catalog:cart")
        if get_checkout_service_type(request) != CustomerOrder.SERVICE_DELIVERY:
            return redirect("catalog:invoice")
        profile, addresses = get_checkout_addresses(request)
        addresses = addresses.filter(area__is_active=True)
        addresses = attach_address_delivery_fee_display(addresses, get_language(request), cart)
        if request.POST.get("address") == "__add_new__":
            form = self.get_form(request, addresses)
            return self.render_address_step(
                request,
                cart,
                profile,
                addresses,
                form=form,
                selected_address_id=form.initial.get("address"),
                is_address_modal_open=True,
            )
        if request.POST.get("address_action") == "add":
            address_form = self.get_address_form(data=request.POST)
            if address_form.is_valid():
                address = address_form.save(profile=profile)
                set_checkout_address(request, address.pk)
                preserve_cart_for_next_request(request)
                return redirect("catalog:checkout-address")
            form = self.get_form(request, addresses)
            return self.render_address_step(
                request,
                cart,
                profile,
                addresses,
                form=form,
                address_form=address_form,
                selected_address_id=request.POST.get("address"),
                is_address_modal_open=True,
            )
        form = self.get_form(request, addresses, data=request.POST)
        if form.is_valid():
            address = form.cleaned_data["address"]
            set_checkout_address(request, address.pk)
            checkout_summary = build_checkout_summary(request, address, CustomerOrder.SERVICE_DELIVERY)
            order = create_order_from_checkout(profile, address, checkout_summary)
            clear_cart(request)
            messages.success(
                request,
                get_ui_strings(get_language(request))["order_confirmed"].format(invoice_number=order.invoice_number),
            )
            return redirect("catalog:cart")
        return self.render_address_step(
            request,
            cart,
            profile,
            addresses,
            form=form,
            selected_address_id=request.POST.get("address"),
        )


class InvoiceView(LoginRequiredMixin, TemplateView):
    template_name = "public/invoice.html"
    login_url = "core:login"

    def dispatch(self, request, *args, **kwargs):
        if not build_cart(request)["items"]:
            return redirect("catalog:cart")
        self.service_type = get_checkout_service_type(request)
        self.selected_address = None
        if self.service_type == CustomerOrder.SERVICE_DELIVERY:
            _, addresses = get_checkout_addresses(request)
            selected_address = get_selected_checkout_address(request, addresses)
            if selected_address is None:
                messages.info(request, get_ui_strings(get_language(request))["add_address_before_checkout"])
                preserve_cart_for_next_request(request)
                return redirect("catalog:checkout-address")
            set_checkout_address(request, selected_address.pk)
            self.selected_address = selected_address
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        checkout_summary = build_checkout_summary(
            self.request,
            self.selected_address,
            self.service_type,
        )
        context.update(checkout_summary)
        context["invoice_number"] = timezone.now().strftime("AR-%Y%m%d-%H%M")
        context["invoice_date"] = timezone.localtime()
        return context


class CheckoutConfirmView(LoginRequiredMixin, View):
    login_url = "core:login"

    def post(self, request):
        cart = build_cart(request)
        if not cart["items"]:
            return redirect("catalog:cart")

        service_type = get_checkout_service_type(request)
        profile, addresses = get_checkout_addresses(request)
        selected_address = None
        if service_type == CustomerOrder.SERVICE_DELIVERY:
            selected_address = get_selected_checkout_address(request, addresses)
            if selected_address is None:
                messages.info(request, get_ui_strings(get_language(request))["select_address_first"])
                return redirect("catalog:checkout-address")

        checkout_summary = build_checkout_summary(request, selected_address, service_type)
        order = create_order_from_checkout(profile, selected_address, checkout_summary)
        clear_cart(request)
        messages.success(
            request,
            get_ui_strings(get_language(request))["order_confirmed"].format(invoice_number=order.invoice_number),
        )
        return redirect("catalog:cart")
