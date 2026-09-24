from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.core.validators import safe_image_path, safe_resume_path, validate_safe_image, validate_safe_pdf


class PublishableQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=PublicationStatus.PUBLISHED)


class PublicationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class PublicationModel(TimeStampedModel):
    status = models.CharField(max_length=12, choices=PublicationStatus.choices, default=PublicationStatus.DRAFT, db_index=True)

    objects = PublishableQuerySet.as_manager()

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    full_name = models.CharField(max_length=100)
    professional_title = models.CharField(max_length=160)
    hero_eyebrow = models.CharField(max_length=80, blank=True)
    hero_statement = models.CharField(max_length=220)
    hero_supporting_text = models.TextField(max_length=600, blank=True)
    about_heading = models.CharField(max_length=120, blank=True)
    about_body = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to=safe_image_path, blank=True, validators=[validate_safe_image])
    resume = models.FileField(upload_to=safe_resume_path, blank=True, validators=[validate_safe_pdf])

    class Meta:
        permissions = [("manage_profile", "Can manage the public profile")]

    def __str__(self) -> str:
        return self.full_name


class Technology(TimeStampedModel):
    class Category(models.TextChoices):
        FRONTEND = "frontend", "Frontend"
        BACKEND = "backend", "Backend"
        DATABASE = "database", "Databases"
        API = "api", "APIs"
        AUTOMATION = "automation", "Automation"
        DEVOPS = "devops", "DevOps"
        TOOL = "tool", "Tools"

    name = models.CharField(max_length=64, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("category", "sort_order", "name")

    def __str__(self) -> str:
        return self.name


class Skill(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    category = models.CharField(max_length=24, choices=Technology.Category.choices)
    description = models.CharField(max_length=240, blank=True)
    technologies = models.ManyToManyField(Technology, blank=True, related_name="skills")
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("category", "sort_order", "name")

    def __str__(self) -> str:
        return self.name


class Service(TimeStampedModel):
    title = models.CharField(max_length=100, unique=True)
    summary = models.CharField(max_length=280)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "title")

    def __str__(self) -> str:
        return self.title


class ProjectCategory(TimeStampedModel):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name_plural = "project categories"

    def __str__(self) -> str:
        return self.name


class Project(PublicationModel):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    summary = models.CharField(max_length=360)
    problem = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    features = models.TextField(blank=True, help_text="Use short, truthful paragraphs or a concise list.")
    role = models.CharField(max_length=160, blank=True)
    challenges = models.TextField(blank=True)
    results = models.TextField(blank=True, help_text="Only include substantiated outcomes.")
    category = models.ForeignKey(ProjectCategory, on_delete=models.PROTECT, related_name="projects", null=True, blank=True)
    technologies = models.ManyToManyField(Technology, related_name="projects", blank=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1990), MaxValueValidator(timezone.now().year + 1)], null=True, blank=True
    )
    is_featured = models.BooleanField(default=False, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("-is_featured", "sort_order", "-year", "title")
        indexes = [models.Index(fields=["status", "is_featured", "sort_order"], name="project_public_idx")]
        permissions = [("publish_project", "Can publish projects")]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("portfolio:project-detail", kwargs={"slug": self.slug})


class ProjectImage(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=safe_image_path, validators=[validate_safe_image])
    alt_text = models.CharField(max_length=160, help_text="Describe the image for visitors who cannot see it.")
    caption = models.CharField(max_length=240, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "id")
        constraints = [models.UniqueConstraint(fields=["project", "sort_order"], name="unique_project_image_order")]

    def __str__(self) -> str:
        return f"{self.project} image {self.sort_order}"


class Experience(TimeStampedModel):
    company = models.CharField(max_length=140)
    position = models.CharField(max_length=140)
    description = models.TextField()
    technologies = models.ManyToManyField(Technology, blank=True, related_name="experiences")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("-is_current", "-start_date", "sort_order")
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(end_date__gte=models.F("start_date")),
                name="experience_end_after_start",
            )
        ]

    def clean(self):
        if self.is_current and self.end_date:
            raise ValidationError({"end_date": "A current role cannot have an end date."})

    def __str__(self) -> str:
        return f"{self.position} — {self.company}"


class Education(TimeStampedModel):
    institution = models.CharField(max_length=160)
    qualification = models.CharField(max_length=160)
    field_of_study = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("-end_date", "-start_date", "sort_order")
        constraints = [
            models.CheckConstraint(
                condition=Q(start_date__isnull=True) | Q(end_date__isnull=True) | Q(end_date__gte=models.F("start_date")),
                name="education_end_after_start",
            )
        ]

    def __str__(self) -> str:
        return f"{self.qualification} — {self.institution}"


class Certification(TimeStampedModel):
    name = models.CharField(max_length=160)
    issuer = models.CharField(max_length=160)
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("-issued_date", "sort_order", "name")
        constraints = [
            models.CheckConstraint(
                condition=Q(issued_date__isnull=True) | Q(expiry_date__isnull=True) | Q(expiry_date__gte=models.F("issued_date")),
                name="certification_expiry_after_issued",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} — {self.issuer}"


class SocialLink(TimeStampedModel):
    label = models.CharField(max_length=50, unique=True)
    url = models.URLField()
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "label")

    def __str__(self) -> str:
        return self.label
