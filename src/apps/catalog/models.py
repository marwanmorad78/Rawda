import re

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from apps.core.models import TimeStampedModel
from media.utils.image_optimizer import OptimizedImageField


def category_upload_path(instance, filename):
    return f"categories/{filename}"


def product_upload_path(instance, filename):
    return f"products/{filename}"


def company_upload_path(instance, filename):
    return f"product-companies/{filename}"


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
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="subcategories",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=120)
    name_ar = models.CharField(max_length=120, blank=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    sold_by_weight = models.BooleanField(null=True, blank=True, default=None)
    is_price_linked_to_dollar = models.BooleanField(null=True, blank=True, default=None)
    cover_image = OptimizedImageField(
        upload_to=category_upload_path,
        optimization_profile="category",
        blank=True,
    )
    external_image_url = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["parent", "is_active", "display_order"]),
            models.Index(fields=["is_active", "display_order"]),
        ]

    def clean(self):
        super().clean()
        if self.parent_id and self.parent_id == self.pk:
            raise ValidationError({"parent": "A category cannot be its own parent."})

        ancestor = self.parent
        while ancestor is not None:
            if ancestor.pk == self.pk:
                raise ValidationError({"parent": "A category cannot use one of its subcategories as parent."})
            ancestor = ancestor.parent

    def get_effective_setting(self, field_name, default=False):
        value = getattr(self, field_name)
        if value is not None:
            return value
        if self.parent_id:
            return self.parent.get_effective_setting(field_name, default)
        return default

    @property
    def effective_sold_by_weight(self):
        return self.get_effective_setting("sold_by_weight")

    @property
    def effective_is_price_linked_to_dollar(self):
        return self.get_effective_setting("is_price_linked_to_dollar")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(Category, self.name, "category", self.pk)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category-detail", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    PRODUCT_TYPE_NORMAL = "normal"
    PRODUCT_TYPE_COMPANY_GROUPED = "company_grouped"
    PRODUCT_TYPE_CHOICES = [
        (PRODUCT_TYPE_NORMAL, "Normal product"),
        (PRODUCT_TYPE_COMPANY_GROUPED, "Company/brand grouped product"),
    ]

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
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    product_type = models.CharField(
        max_length=24,
        choices=PRODUCT_TYPE_CHOICES,
        default=PRODUCT_TYPE_NORMAL,
    )
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
    has_options = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sku = models.CharField(max_length=50, blank=True)
    primary_image = OptimizedImageField(
        upload_to=product_upload_path,
        optimization_profile="product",
        blank=True,
    )
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
        if not self.sku or (self.pk and previous_category_id != self.category_id):
            self.sku = self._next_category_sku()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product-detail", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.name

    @property
    def is_company_grouped(self):
        return self.product_type == self.PRODUCT_TYPE_COMPANY_GROUPED


class ProductOption(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="options")
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_default = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name", "id"]
        indexes = [models.Index(fields=["product", "is_available", "display_order"])]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            ProductOption.objects.filter(product=self.product, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.name}"


class Company(TimeStampedModel):
    code = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=120)
    logo = OptimizedImageField(
        upload_to=company_upload_path,
        optimization_profile="company",
        blank=True,
    )
    external_logo_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["display_order", "name", "id"]
        indexes = [models.Index(fields=["is_active", "display_order"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class ProductCompany(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="companies")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="products")
    is_price_linked_to_dollar = models.BooleanField(null=True, blank=True, default=None)

    class Meta:
        verbose_name = "Product company"
        verbose_name_plural = "Product companies"
        ordering = ["company__display_order", "company__name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "company"],
                name="unique_product_company",
            )
        ]
        indexes = [models.Index(fields=["product", "company"])]

    @property
    def code(self):
        return self.company.code

    @property
    def name(self):
        return self.company.name

    @property
    def logo(self):
        return self.company.logo

    @property
    def external_logo_url(self):
        return self.company.external_logo_url

    @property
    def is_active(self):
        return self.company.is_active

    @property
    def order(self):
        return self.company.display_order

    @property
    def effective_is_price_linked_to_dollar(self):
        if self.is_price_linked_to_dollar is not None:
            return self.is_price_linked_to_dollar
        from apps.core.pricing import product_uses_dollar_price

        return product_uses_dollar_price(self.product)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.company.name}"


class ProductCompanyOption(TimeStampedModel):
    company = models.ForeignKey(ProductCompany, on_delete=models.CASCADE, related_name="options")
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Product company option"
        verbose_name_plural = "Product company options"
        ordering = ["order", "name", "id"]
        indexes = [models.Index(fields=["company", "is_available", "order"])]

    def __str__(self) -> str:
        return f"{self.company.name} - {self.name}"


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery_images")
    image = OptimizedImageField(
        upload_to=gallery_upload_path,
        optimization_profile="product",
    )
    alt_text = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.product.name} image"
