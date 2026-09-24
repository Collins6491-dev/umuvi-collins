from django.core.validators import MaxLengthValidator
from django.db import models

from apps.core.models import TimeStampedModel


class ContactSubmission(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        READ = "read", "Read"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=160, blank=True)
    message = models.TextField(max_length=4000, validators=[MaxLengthValidator(4000)])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW, db_index=True)
    source_fingerprint = models.CharField(max_length=64, blank=True, editable=False)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["status", "-created_at"], name="contact_status_idx")]
        permissions = [("manage_submission", "Can manage contact submissions")]

    def __str__(self) -> str:
        return f"{self.name}: {self.subject or 'Contact request'}"
