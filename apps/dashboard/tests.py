from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from apps.portfolio.models import Project


class DashboardAuthorizationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="viewer", password="a-secure-password-123")
        self.staff_user = User.objects.create_user(username="staff", password="a-secure-password-123", is_staff=True)
        self.view_project = Permission.objects.get(codename="view_project")
        self.staff_user.user_permissions.add(self.view_project)
        self.project = Project.objects.create(title="Private", slug="private", summary="Private project")

    def test_dashboard_redirects_anonymous_people_to_login(self):
        response = self.client.get(reverse("dashboard:overview"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_authenticated_non_staff_user_is_forbidden(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard:overview"))
        self.assertEqual(response.status_code, 403)

    def test_staff_member_cannot_create_without_add_permission(self):
        self.client.force_login(self.staff_user)
        list_response = self.client.get(reverse("dashboard:content-list", kwargs={"key": "projects"}))
        self.assertEqual(list_response.status_code, 200)
        self.assertNotContains(list_response, "Add Project")
        create_response = self.client.get(reverse("dashboard:content-create", kwargs={"key": "projects"}))
        self.assertEqual(create_response.status_code, 403)

    def test_staff_member_with_only_view_permission_cannot_edit_object_by_id(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("dashboard:content-update", kwargs={"key": "projects", "pk": self.project.pk}))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_header_has_a_post_logout_control(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("dashboard:overview"))
        self.assertContains(response, "Log out")
        self.assertContains(response, f'action="{reverse("accounts:logout")}"')

        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
