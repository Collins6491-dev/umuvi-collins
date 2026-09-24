from django.core.validators import MaxLengthValidator
from django.db import models

from .validators import safe_image_path, validate_safe_image


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(TimeStampedModel):
    """One editable site-level settings record, surfaced through the custom dashboard."""

    site_name = models.CharField(max_length=120, default="Portfolio")
    site_url = models.URLField(blank=True, help_text="Canonical production URL, without a trailing slash.")
    default_meta_title = models.CharField(max_length=60, blank=True)
    default_meta_description = models.CharField(max_length=160, blank=True, validators=[MaxLengthValidator(160)])
    og_image = models.ImageField(upload_to=safe_image_path, blank=True, validators=[validate_safe_image])
    contact_email = models.EmailField(blank=True)
    primary_cta_label = models.CharField(max_length=40, default="View selected work")
    secondary_cta_label = models.CharField(max_length=40, default="Get in touch")

    class Meta:
        verbose_name_plural = "site settings"

    def __str__(self) -> str:
        return self.site_name


class SectionConfiguration(TimeStampedModel):
    class Section(models.TextChoices):
        ABOUT = "about", "About"
        SKILLS = "skills", "Skills"
        SERVICES = "services", "Services"
        PROJECTS = "projects", "Projects"
        EXPERIENCE = "experience", "Experience"
        EDUCATION = "education", "Education"
        CERTIFICATIONS = "certifications", "Certifications"
        CONTACT = "contact", "Contact"

    section = models.CharField(max_length=24, choices=Section.choices, unique=True)
    is_visible = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "section")

    def __str__(self) -> str:
        return self.get_section_display()
