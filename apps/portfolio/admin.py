from django.contrib import admin

from .models import (
    Certification,
    Education,
    Experience,
    Profile,
    Project,
    ProjectCategory,
    ProjectImage,
    Service,
    Skill,
    SocialLink,
    Technology,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "is_featured", "year", "updated_at")
    list_filter = ("status", "is_featured", "category")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("technologies",)


admin.site.register([Profile, Technology, Skill, Service, ProjectCategory, ProjectImage, Experience, Education, Certification, SocialLink])
