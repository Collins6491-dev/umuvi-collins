from django.test import TestCase
from django.urls import reverse

from apps.core.models import SiteSettings

from .models import Profile, Project, Service, SocialLink


class PortfolioVisibilityTests(TestCase):
    def setUp(self):
        self.draft = Project.objects.create(title="Internal draft", slug="internal-draft", summary="Not ready yet.")
        self.public = Project.objects.create(
            title="Published project", slug="published-project", summary="A published project.", status="published"
        )

    def test_draft_case_study_is_not_publicly_resolvable(self):
        response = self.client.get(reverse("portfolio:project-detail", kwargs={"slug": self.draft.slug}))
        self.assertEqual(response.status_code, 404)

    def test_published_case_study_is_publicly_resolvable(self):
        response = self.client.get(reverse("portfolio:project-detail", kwargs={"slug": self.public.slug}))
        self.assertContains(response, self.public.title)

    def test_resume_returns_404_when_no_resume_is_published(self):
        self.assertEqual(self.client.get(reverse("portfolio:download-resume")).status_code, 404)

    def test_public_footer_uses_dashboard_managed_profile_contact_service_and_social_data(self):
        Profile.objects.create(
            full_name="Ada Example",
            professional_title="Software Engineer",
            hero_statement="Useful software, thoughtfully built.",
            hero_supporting_text="Building secure web applications.",
        )
        SiteSettings.objects.create(site_name="Ada Example", contact_email="ada@example.test")
        Service.objects.create(title="Django development", summary="Web applications")
        SocialLink.objects.create(label="GitHub", url="https://github.com/example")

        response = self.client.get(reverse("portfolio:home"))

        self.assertContains(response, "Ada Example")
        self.assertContains(response, "Software Engineer")
        self.assertContains(response, "ada@example.test")
        self.assertContains(response, "Django development")
        self.assertContains(response, "https://github.com/example")
        self.assertContains(response, "Footer navigation")

    def test_public_footer_is_available_on_project_detail_pages(self):
        response = self.client.get(reverse("portfolio:project-detail", kwargs={"slug": self.public.slug}))

        self.assertContains(response, 'class="site-footer"')
