import re

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from apps.core.models import TimeStampedModel


def category_upload_path(instance, filename):
    return f"categories/{filename}"


def product_upload_path(instance, filename):
    return f"products/{filename}"


def gallery_upload_path(instance, filename):
    return f"products/gallery/{filename}"


def _generate_unique_slug(model_class, value, fallback_prefix, instance_pk=None):
    base_slug = slugify(value or "")
    if not base_slug:
        base_slug = fallback_prefix
    candidate = base_slug
    counter = 2
    while model_class.objects.exclude(pk=instance_pk).filter(slug=candidate).exists():
        candidate = f"{base_slug}-{counter}"
        counter += 1
    return candidate


class Category(TimeStampedModel):
    name = models.CharField(max_length=120)
    name_ar = models.CharField(max_length=120, blank=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    sold_by_weight = models.BooleanField(default=False)
    is_price_linked_to_dollar = models.BooleanField(default=False)
    cover_image = models.ImageField(upload_to=category_upload_path, blank=True)
    external_image_url = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["display_order", "name"]
        indexes = [models.Index(fields=["is_active", "display_order"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(Category, self.name, "category", self.pk)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category-detail", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    BEHAVIOR_INHERIT = "inherit"
    BEHAVIOR_CUSTOM = "custom"
    BEHAVIOR_CHOICES = [
        (BEHAVIOR_INHERIT, "Inherit from category"),
        (BEHAVIOR_CUSTOM, "Custom product setting"),
    ]

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=150)
    name_ar = models.CharField(max_length=150, blank=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    short_description = models.CharField(max_length=280, blank=True)
    short_description_ar = models.CharField(max_length=280, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_link_mode = models.CharField(
        max_length=20,
        choices=BEHAVIOR_CHOICES,
        default=BEHAVIOR_INHERIT,
    )
    is_price_linked_to_dollar = models.BooleanField(default=False)
    unit_label = models.CharField(max_length=50, default="per item")
    unit_label_ar = models.CharField(max_length=50, blank=True)
    sold_by_weight_mode = models.CharField(
        max_length=20,
        choices=BEHAVIOR_CHOICES,
        default=BEHAVIOR_INHERIT,
    )
    sold_by_weight = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sku = models.CharField(max_length=50, blank=True)
    primary_image = models.ImageField(upload_to=product_upload_path, blank=True)
    external_image_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["category", "is_available"]),
            models.Index(fields=["is_featured", "is_available"]),
        ]

    def _sku_prefix(self):
        base = slugify(self.category.name or "") if self.category_id else ""
        letters_only = re.sub(r"[^A-Za-z]", "", base).upper()
        return (letters_only[:3] or "CAT").ljust(3, "X")

    def _next_category_sku(self):
        prefix = self._sku_prefix()
        pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
        existing_skus = (
            Product.objects.filter(category=self.category)
            .exclude(pk=self.pk)
            .values_list("sku", flat=True)
        )
        last_number = 0
        for sku in existing_skus:
            match = pattern.match(sku or "")
            if match:
                last_number = max(last_number, int(match.group(1)))
        return f"{prefix}-{last_number + 1}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(Product, self.name, "product", self.pk)
        previous_category_id = None
        if self.pk:
            previous_category_id = (
                Product.objects.filter(pk=self.pk).values_list("category_id", flat=True).first()
            )
        if not self.sku or previous_category_id != self.category_id:
            self.sku = self._next_category_sku()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product-detail", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.name


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to=gallery_upload_path)
    alt_text = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.product.name} image"
