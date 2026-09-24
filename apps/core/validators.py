from __future__ import annotations

import os
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image, UnidentifiedImageError


MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_RESUME_BYTES = 8 * 1024 * 1024
IMAGE_FORMATS = {"JPEG": {"jpg", "jpeg"}, "PNG": {"png"}, "WEBP": {"webp"}, "AVIF": {"avif"}}
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/avif"}


def _extension(uploaded_file) -> str:
    return os.path.splitext(uploaded_file.name)[1].lower().lstrip(".")


def validate_safe_image(uploaded_file) -> None:
    """Validate size, declared type, decoded image content, and real image format."""
    if uploaded_file.size > MAX_IMAGE_BYTES:
        raise ValidationError("Images must be 5 MB or smaller.")

    extension = _extension(uploaded_file)
    allowed_extensions = {suffix for values in IMAGE_FORMATS.values() for suffix in values}
    if extension not in allowed_extensions:
        raise ValidationError("Use a JPEG, PNG, WebP, or AVIF image.")

    declared_type = getattr(uploaded_file, "content_type", "")
    if declared_type and declared_type not in IMAGE_CONTENT_TYPES:
        raise ValidationError("The uploaded file has an invalid image MIME type.")

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image.verify()
        real_format = image.format
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ValidationError("The uploaded file is not a valid image.") from exc
    finally:
        uploaded_file.seek(0)

    if real_format not in IMAGE_FORMATS or extension not in IMAGE_FORMATS[real_format]:
        raise ValidationError("The file extension does not match its image content.")


def validate_safe_pdf(uploaded_file) -> None:
    if uploaded_file.size > MAX_RESUME_BYTES:
        raise ValidationError("Resumes must be 8 MB or smaller.")
    if _extension(uploaded_file) != "pdf":
        raise ValidationError("Only PDF resumes are accepted.")
    declared_type = getattr(uploaded_file, "content_type", "")
    if declared_type and declared_type not in {"application/pdf", "application/x-pdf"}:
        raise ValidationError("The uploaded file has an invalid PDF MIME type.")
    try:
        uploaded_file.seek(0)
        signature = uploaded_file.read(5)
    finally:
        uploaded_file.seek(0)
    if signature != b"%PDF-":
        raise ValidationError("The uploaded file is not a valid PDF document.")


def safe_image_path(instance, filename: str) -> str:
    extension = _extension(type("Upload", (), {"name": filename})())
    return f"images/{uuid.uuid4().hex}.{extension}"


def safe_resume_path(instance, filename: str) -> str:
    return f"resumes/{uuid.uuid4().hex}.pdf"


image_extension_validator = FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp", "avif"])
pdf_extension_validator = FileExtensionValidator(allowed_extensions=["pdf"])
