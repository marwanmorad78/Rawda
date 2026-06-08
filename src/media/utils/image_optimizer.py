from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from django.core.files.base import ContentFile
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from PIL import Image, ImageOps


@dataclass(frozen=True)
class ImageOptimizationProfile:
    max_dimension: int
    quality: int


@dataclass(frozen=True)
class ImageOptimizationResult:
    content: bytes
    filename: str
    original_size: int
    optimized_size: int
    original_dimensions: tuple[int, int]
    optimized_dimensions: tuple[int, int]

    @property
    def space_saved(self) -> int:
        return self.original_size - self.optimized_size


IMAGE_PROFILES: dict[str, ImageOptimizationProfile] = {
    "product": ImageOptimizationProfile(max_dimension=800, quality=80),
    "category": ImageOptimizationProfile(max_dimension=1000, quality=85),
    "company": ImageOptimizationProfile(max_dimension=500, quality=85),
    "banner": ImageOptimizationProfile(max_dimension=1400, quality=80),
}


def _webp_filename(filename: str) -> str:
    name = Path(filename or "image").name
    stem = Path(name).stem or "image"
    return f"{stem}.webp"


def optimize_image_file(
    image_file: BinaryIO,
    filename: str,
    *,
    max_dimension: int,
    quality: int,
) -> ImageOptimizationResult:
    """Convert one image stream to resized, EXIF-corrected WebP bytes."""
    if hasattr(image_file, "seek"):
        image_file.seek(0)
    original_content = image_file.read()
    if not original_content:
        raise ValueError("The image file is empty.")

    with Image.open(BytesIO(original_content)) as source:
        source.load()
        original_dimensions = source.size
        image = ImageOps.exif_transpose(source)

        has_transparency = image.mode in {"RGBA", "LA"} or (
            image.mode == "P" and "transparency" in image.info
        )
        image = image.convert("RGBA" if has_transparency else "RGB")
        image.thumbnail(
            (max_dimension, max_dimension),
            Image.Resampling.LANCZOS,
        )
        optimized_dimensions = image.size

        output = BytesIO()
        image.save(
            output,
            format="WEBP",
            quality=quality,
            method=6,
            optimize=True,
            lossless=False,
            exact=has_transparency,
        )

    content = output.getvalue()
    return ImageOptimizationResult(
        content=content,
        filename=_webp_filename(filename),
        original_size=len(original_content),
        optimized_size=len(content),
        original_dimensions=original_dimensions,
        optimized_dimensions=optimized_dimensions,
    )


def optimize_image(
    image_path: str | Path,
    *,
    max_dimension: int = 800,
    quality: int = 80,
    output_path: str | Path | None = None,
) -> ImageOptimizationResult:
    """Optimize a local image path and write a WebP file beside it by default."""
    source_path = Path(image_path)
    target_path = Path(output_path) if output_path else source_path.with_suffix(".webp")
    with source_path.open("rb") as image_file:
        result = optimize_image_file(
            image_file,
            source_path.name,
            max_dimension=max_dimension,
            quality=quality,
        )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(result.content)
    return result


class OptimizedImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        profile = IMAGE_PROFILES[self.field.optimization_profile]
        result = optimize_image_file(
            content,
            name,
            max_dimension=profile.max_dimension,
            quality=profile.quality,
        )
        super().save(
            result.filename,
            ContentFile(result.content),
            save=save,
        )


class OptimizedImageField(models.ImageField):
    """ImageField that writes only an optimized WebP version of new uploads."""

    attr_class = OptimizedImageFieldFile

    def __init__(self, *args, optimization_profile: str, **kwargs):
        if optimization_profile not in IMAGE_PROFILES:
            raise ValueError(f"Unknown image optimization profile: {optimization_profile}")
        self.optimization_profile = optimization_profile
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["optimization_profile"] = self.optimization_profile
        return name, path, args, kwargs
