from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(TimeStampedModel):
    store_name = models.CharField(max_length=150)
    store_name_ar = models.CharField(max_length=150, blank=True)
    tagline = models.CharField(max_length=255, blank=True)
    tagline_ar = models.CharField(max_length=255, blank=True)
    about_text = models.TextField()
    about_text_ar = models.TextField(blank=True)
    address = models.TextField()
    address_ar = models.TextField(blank=True)
    primary_phone = models.CharField(max_length=30)
    secondary_phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    working_hours_summary = models.CharField(max_length=255, blank=True)
    working_hours_summary_ar = models.CharField(max_length=255, blank=True)
    hero_title = models.CharField(max_length=150)
    hero_title_ar = models.CharField(max_length=150, blank=True)
    hero_subtitle = models.TextField(blank=True)
    hero_subtitle_ar = models.TextField(blank=True)
    hero_cta_text = models.CharField(max_length=80, blank=True)
    hero_cta_text_ar = models.CharField(max_length=80, blank=True)
    hero_cta_url = models.CharField(max_length=255, blank=True)
    dollar_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def clean(self) -> None:
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("Only one SiteSettings record is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.store_name


class BusinessHour(TimeStampedModel):
    DAYS = [
        (0, "Sunday"),
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
    ]

    site_settings = models.ForeignKey(
        SiteSettings, on_delete=models.CASCADE, related_name="business_hours"
    )
    day_of_week = models.PositiveSmallIntegerField(choices=DAYS)
    label = models.CharField(max_length=40)
    label_ar = models.CharField(max_length=40, blank=True)
    open_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "day_of_week"]
        unique_together = ("site_settings", "day_of_week")

    def __str__(self) -> str:
        return self.label


class SocialLink(TimeStampedModel):
    site_settings = models.ForeignKey(
        SiteSettings, on_delete=models.CASCADE, related_name="social_links"
    )
    platform = models.CharField(max_length=50)
    url = models.URLField()
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "platform"]

    def __str__(self) -> str:
        return self.platform


class DeliveryArea(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    has_sub_areas = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "name"]
        indexes = [models.Index(fields=["is_active", "display_order"])]

    def __str__(self) -> str:
        return self.name


class DeliverySubArea(TimeStampedModel):
    area = models.ForeignKey(
        DeliveryArea,
        on_delete=models.CASCADE,
        related_name="sub_areas",
    )
    name = models.CharField(max_length=150)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "name"]
        unique_together = ("area", "name")
        indexes = [models.Index(fields=["area", "is_active", "display_order"])]

    def __str__(self) -> str:
        return f"{self.area.name} - {self.name}"


class CustomerProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ["full_name", "phone_number"]

    def __str__(self) -> str:
        return self.full_name or self.phone_number


class CustomerAddress(TimeStampedModel):
    profile = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    area = models.ForeignKey(
        DeliveryArea,
        on_delete=models.PROTECT,
        related_name="addresses",
    )
    sub_area = models.ForeignKey(
        DeliverySubArea,
        on_delete=models.PROTECT,
        related_name="addresses",
        blank=True,
        null=True,
    )
    street_address = models.CharField(max_length=255)
    building = models.CharField(max_length=80, blank=True)
    floor = models.CharField(max_length=40, blank=True)
    apartment = models.CharField(max_length=40, blank=True)
    nearby_landmark = models.CharField(max_length=180, blank=True)
    notes = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "-updated_at", "id"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        siblings = type(self).objects.filter(profile=self.profile).exclude(pk=self.pk)
        if self.is_default:
            siblings.update(is_default=False)
        elif not siblings.filter(is_default=True).exists():
            type(self).objects.filter(pk=self.pk).update(is_default=True)
            self.is_default = True

    def __str__(self) -> str:
        area_label = self.area.name
        if self.sub_area_id:
            area_label = f"{area_label} / {self.sub_area.name}"
        return f"{area_label} - {self.street_address}"


class CustomerOrder(TimeStampedModel):
    SERVICE_PICKUP = "pickup"
    SERVICE_DELIVERY = "delivery"
    STATUS_WAITING_ACCEPT = "waiting_accept"
    STATUS_BEING_PREPARED = "being_prepared"
    STATUS_OUT_FOR_DELIVERY = "out_for_delivery"
    STATUS_READY_TO_PICKUP = "ready_to_pickup"
    STATUS_DONE = "done"
    STATUS_CANCELLED = "cancelled"
    STATUS_PENDING = STATUS_WAITING_ACCEPT
    STATUS_CONFIRMED = STATUS_DONE
    SERVICE_CHOICES = [
        (SERVICE_PICKUP, "Pickup"),
        (SERVICE_DELIVERY, "Delivery"),
    ]
    STATUS_CHOICES = [
        (STATUS_WAITING_ACCEPT, "Waiting for accept"),
        (STATUS_BEING_PREPARED, "Being prepared"),
        (STATUS_OUT_FOR_DELIVERY, "Out for delivery"),
        (STATUS_READY_TO_PICKUP, "Ready to pick up"),
        (STATUS_DONE, "Done"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    ACTIVE_STATUSES = [
        STATUS_WAITING_ACCEPT,
        STATUS_BEING_PREPARED,
        STATUS_OUT_FOR_DELIVERY,
        STATUS_READY_TO_PICKUP,
    ]
    DELIVERY_STATUS_FLOW = [
        STATUS_WAITING_ACCEPT,
        STATUS_BEING_PREPARED,
        STATUS_OUT_FOR_DELIVERY,
        STATUS_DONE,
    ]
    PICKUP_STATUS_FLOW = [
        STATUS_WAITING_ACCEPT,
        STATUS_BEING_PREPARED,
        STATUS_READY_TO_PICKUP,
        STATUS_DONE,
    ]

    profile = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    address = models.ForeignKey(
        CustomerAddress,
        on_delete=models.PROTECT,
        related_name="orders",
        blank=True,
        null=True,
    )
    invoice_number = models.CharField(max_length=40, unique=True)
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_CHOICES,
        default=SERVICE_DELIVERY,
    )
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_WAITING_ACCEPT)
    expected_time_minutes = models.PositiveIntegerField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    address_snapshot = models.TextField()
    subtotal_min = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal_max = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_min = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_max = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return self.invoice_number

    @property
    def order_type(self):
        return self.service_type

    @property
    def is_active(self):
        return self.status in self.ACTIVE_STATUSES

    def get_status_flow(self):
        if self.service_type == self.SERVICE_DELIVERY:
            return self.DELIVERY_STATUS_FLOW
        return self.PICKUP_STATUS_FLOW

    def get_next_status(self):
        flow = self.get_status_flow()
        if self.status not in flow:
            return None
        next_index = flow.index(self.status) + 1
        if next_index >= len(flow):
            return None
        return flow[next_index]


class CustomerOrderItem(TimeStampedModel):
    order = models.ForeignKey(
        CustomerOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )
    item_type = models.CharField(max_length=20)
    cart_item_id = models.PositiveIntegerField(blank=True, null=True)
    title = models.CharField(max_length=180)
    category_label = models.CharField(max_length=120, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_label = models.CharField(max_length=50, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total_min = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total_max = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_weight_based = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.title
