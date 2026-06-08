from __future__ import annotations

import logging
import posixpath
from dataclasses import dataclass

from django.apps import apps
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import timezone

from media.utils.image_optimizer import (
    IMAGE_PROFILES,
    OptimizedImageField,
    optimize_image_file,
)

logger = logging.getLogger(__name__)


@dataclass
class OptimizationSummary:
    total_scanned: int = 0
    optimized: int = 0
    skipped: int = 0
    failed: int = 0
    space_saved: int = 0


def format_bytes(value: int) -> str:
    sign = "-" if value < 0 else ""
    size = float(abs(value))
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{sign}{size:.1f} {unit}"
        size /= 1024
    return f"{sign}{size:.1f} GB"


def get_optimized_image_fields():
    for model in apps.get_models():
        for field in model._meta.get_fields():
            if isinstance(field, OptimizedImageField):
                yield model, field


def get_pending_images(model, field):
    return (
        model._default_manager.exclude(**{field.name: ""})
        .exclude(**{f"{field.name}__isnull": True})
        .exclude(**{f"{field.name}__iendswith": ".webp"})
    )


def image_update_values(instance, field, filename):
    values = {field.name: filename}
    if any(model_field.name == "updated_at" for model_field in instance._meta.fields):
        values["updated_at"] = timezone.now()
    return values


class Command(BaseCommand):
    help = "Convert existing uploaded images to resized WebP files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            help="Process at most this many image records.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Inspect and optimize in memory without changing files or database records.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        dry_run = options["dry_run"]
        if limit is not None and limit < 1:
            self.stderr.write(self.style.ERROR("--limit must be a positive integer."))
            return

        image_fields = list(get_optimized_image_fields())
        total_available = sum(
            get_pending_images(model, field).count()
            for model, field in image_fields
        )
        target_total = min(total_available, limit) if limit else total_available
        summary = OptimizationSummary()
        converted_files: dict[tuple[int, str], str] = {}

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run: no files or database rows will change."))

        for model, field in image_fields:
            if summary.total_scanned >= target_total:
                break
            queryset = (
                get_pending_images(model, field)
                .only("pk", field.name)
                .order_by("pk")
            )
            for instance in queryset.iterator(chunk_size=25):
                if summary.total_scanned >= target_total:
                    break
                summary.total_scanned += 1
                self._process_image(
                    instance,
                    field,
                    summary,
                    target_total,
                    converted_files,
                    dry_run=dry_run,
                )

        action_label = "Would optimize" if dry_run else "Optimized"
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Image optimization complete"))
        self.stdout.write(f"Total scanned: {summary.total_scanned}")
        self.stdout.write(f"{action_label}: {summary.optimized}")
        self.stdout.write(f"Skipped: {summary.skipped}")
        self.stdout.write(f"Failed: {summary.failed}")
        self.stdout.write(f"Space saved: {format_bytes(summary.space_saved)}")

    def _process_image(
        self,
        instance,
        field: OptimizedImageField,
        summary: OptimizationSummary,
        target_total: int,
        converted_files: dict[tuple[int, str], str],
        *,
        dry_run: bool,
    ):
        field_file = getattr(instance, field.name)
        old_name = field_file.name
        progress = f"{summary.total_scanned}/{target_total}"
        label = f"{instance._meta.label}.{field.name} pk={instance.pk}"

        if not old_name:
            summary.skipped += 1
            self.stdout.write(f"Skipped {progress}: {label} has no file.")
            return
        if old_name.lower().endswith(".webp"):
            summary.skipped += 1
            self.stdout.write(f"Skipped {progress}: {old_name} is already WebP.")
            return

        storage = field_file.storage
        conversion_key = (id(storage), old_name)
        converted_name = converted_files.get(conversion_key)
        if converted_name:
            if not dry_run:
                model = instance.__class__
                model._default_manager.filter(pk=instance.pk).update(
                    **image_update_values(instance, field, converted_name)
                )
            summary.optimized += 1
            self.stdout.write(f"Optimized {progress}: reused {converted_name}.")
            return

        try:
            if not storage.exists(old_name):
                summary.skipped += 1
                self.stdout.write(
                    self.style.WARNING(f"Skipped {progress}: missing file {old_name}.")
                )
                return

            profile = IMAGE_PROFILES[field.optimization_profile]
            with storage.open(old_name, "rb") as source:
                result = optimize_image_file(
                    source,
                    old_name,
                    max_dimension=profile.max_dimension,
                    quality=profile.quality,
                )

            new_name = posixpath.join(
                posixpath.dirname(old_name),
                result.filename,
            )
            if dry_run:
                summary.optimized += 1
                summary.space_saved += result.space_saved
                self.stdout.write(
                    f"Would optimize {progress}: {old_name} -> {new_name} "
                    f"({format_bytes(result.space_saved)} saved)."
                )
                return

            saved_name = storage.save(new_name, ContentFile(result.content))
            try:
                with transaction.atomic():
                    instance.__class__._default_manager.filter(pk=instance.pk).update(
                        **image_update_values(instance, field, saved_name)
                    )
            except Exception:
                storage.delete(saved_name)
                raise

            storage.delete(old_name)
            converted_files[conversion_key] = saved_name
            summary.optimized += 1
            summary.space_saved += result.space_saved
            self.stdout.write(
                self.style.SUCCESS(
                    f"Optimized {progress}: {old_name} -> {saved_name} "
                    f"({format_bytes(result.space_saved)} saved)."
                )
            )
        except Exception as exc:
            summary.failed += 1
            logger.exception("Failed to optimize %s (%s)", old_name, label)
            self.stderr.write(
                self.style.ERROR(f"Failed {progress}: {old_name}: {exc}")
            )
