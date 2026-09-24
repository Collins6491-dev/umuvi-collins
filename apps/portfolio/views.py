from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, TemplateView

from apps.core.models import SectionConfiguration

from .models import Certification, Education, Experience, Profile, Project, Service, Skill


def section_visibility() -> dict[str, bool]:
    configured = {item.section: item.is_visible for item in SectionConfiguration.objects.all()}
    return {choice: configured.get(choice, True) for choice, _ in SectionConfiguration.Section.choices}


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visibility = section_visibility()
        context.update(
            {
                "profile": Profile.objects.order_by("id").first(),
                "visible_sections": visibility,
                "skills": Skill.objects.prefetch_related("technologies").all() if visibility["skills"] else Skill.objects.none(),
                "services": Service.objects.filter(is_visible=True) if visibility["services"] else Service.objects.none(),
                "featured_projects": Project.objects.published()
                .select_related("category")
                .prefetch_related("technologies", "images")
                .filter(is_featured=True)[:4]
                if visibility["projects"]
                else Project.objects.none(),
                "projects": Project.objects.published()
                .select_related("category")
                .prefetch_related("technologies", "images")[:8]
                if visibility["projects"]
                else Project.objects.none(),
                "experiences": Experience.objects.prefetch_related("technologies").all()
                if visibility["experience"]
                else Experience.objects.none(),
                "education": Education.objects.all() if visibility["education"] else Education.objects.none(),
                "certifications": Certification.objects.all()
                if visibility["certifications"]
                else Certification.objects.none(),
            }
        )
        return context


class ProjectDetailView(DetailView):
    template_name = "portfolio/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.published().select_related("category").prefetch_related("technologies", "images")


@require_GET
def download_resume(request):
    profile = Profile.objects.exclude(resume="").order_by("id").first()
    if not profile or not profile.resume:
        raise Http404("A resume is not available.")
    response = FileResponse(profile.resume.open("rb"), as_attachment=True, filename="resume.pdf")
    response["X-Content-Type-Options"] = "nosniff"
    return response
