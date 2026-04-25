from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils import timezone

from apps.core.models import TimeStampedModel


def promotion_upload_path(instance, filename):
    return f"promotions/{filename}"


def build_unique_promotion_slug(source_value, instance_pk=None):
    base_slug = slugify(source_value or "") or "promotion"
    slug = base_slug
    suffix = 2
    while Promotion.objects.exclude(pk=instance_pk).filter(slug=slug).exists():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    return slug


class PromotionQuerySet(models.QuerySet):
    def active(self):
        today = timezone.localdate()
        return self.filter(is_active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=today),
            Q(end_date__isnull=True) | Q(end_date__gte=today),
        ).order_by("display_order", "title")


class Promotion(TimeStampedModel):
    title = models.CharField(max_length=140)
    title_ar = models.CharField(max_length=140, blank=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    subtitle_ar = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_price_linked_to_dollar = models.BooleanField(default=False)
    badge_text = models.CharField(max_length=60, blank=True)
    badge_text_ar = models.CharField(max_length=60, blank=True)
    cta_text = models.CharField(max_length=60, blank=True)
    cta_text_ar = models.CharField(max_length=60, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to=promotion_upload_path, blank=True)
    external_image_url = models.URLField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    objects = PromotionQuerySet.as_manager()

    class Meta:
        ordering = ["display_order", "title"]
        indexes = [
            models.Index(fields=["is_active", "display_order"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def save(self, *args, **kwargs):
        if not self.title:
            source_text = self.description or self.description_ar or "Promotion"
            self.title = " ".join(source_text.strip().split())[:140] or "Promotion"
        if not self.slug:
            self.slug = build_unique_promotion_slug(self.title, self.pk)
        return super().save(*args, **kwargs)

    @classmethod
    def active(cls):
        return cls.objects.active()

    def __str__(self) -> str:
        return self.title
