from dataclasses import dataclass

from apps.contact.models import ContactSubmission
from apps.core.models import SectionConfiguration
from apps.portfolio.models import (
    Certification,
    Education,
    Experience,
    Project,
    ProjectCategory,
    ProjectImage,
    Service,
    Skill,
    SocialLink,
    Technology,
)


@dataclass(frozen=True)
class ContentSpec:
    key: str
    label: str
    model: type
    fields: tuple[str, ...]
    table_fields: tuple[str, ...]
    allow_create: bool = True
    allow_delete: bool = True


SPECS = (
    ContentSpec("projects", "Projects", Project, ("title", "slug", "summary", "problem", "solution", "features", "role", "challenges", "results", "category", "technologies", "github_url", "live_url", "year", "is_featured", "sort_order", "status"), ("title", "status", "is_featured", "year")),
    ContentSpec("project-images", "Project images", ProjectImage, ("project", "image", "alt_text", "caption", "sort_order"), ("project", "alt_text", "sort_order")),
    ContentSpec("technologies", "Technologies", Technology, ("name", "category", "sort_order"), ("name", "category", "sort_order")),
    ContentSpec("skills", "Skills", Skill, ("name", "category", "description", "technologies", "sort_order"), ("name", "category", "sort_order")),
    ContentSpec("services", "Services", Service, ("title", "summary", "sort_order", "is_visible"), ("title", "is_visible", "sort_order")),
    ContentSpec("categories", "Project categories", ProjectCategory, ("name", "slug", "sort_order"), ("name", "slug", "sort_order")),
    ContentSpec("experience", "Experience", Experience, ("company", "position", "description", "technologies", "start_date", "end_date", "is_current", "sort_order"), ("company", "position", "is_current", "start_date")),
    ContentSpec("education", "Education", Education, ("institution", "qualification", "field_of_study", "description", "start_date", "end_date", "sort_order"), ("institution", "qualification", "end_date")),
    ContentSpec("certifications", "Certifications", Certification, ("name", "issuer", "issued_date", "expiry_date", "credential_url", "sort_order"), ("name", "issuer", "issued_date")),
    ContentSpec("social-links", "Social links", SocialLink, ("label", "url", "sort_order", "is_visible"), ("label", "is_visible", "sort_order")),
    ContentSpec("sections", "Section visibility", SectionConfiguration, ("section", "is_visible", "sort_order"), ("section", "is_visible", "sort_order")),
    ContentSpec("messages", "Contact messages", ContactSubmission, ("status",), ("name", "email", "subject", "status", "created_at"), allow_create=False, allow_delete=False),
)

BY_KEY = {spec.key: spec for spec in SPECS}
