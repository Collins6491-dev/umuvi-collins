from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class AccountFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboard-user",
            email="dashboard@example.com",
            password="a-secure-password-123",
            is_staff=True,
        )

    def test_logout_invalidates_the_session_and_returns_to_login(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_sends_a_signed_reset_link_for_an_active_account(self):
        response = self.client.post(reverse("accounts:password-reset"), {"email": self.user.email})

        self.assertRedirects(response, reverse("accounts:password-reset-done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("http://localhost:8000/account/reset/", mail.outbox[0].body)
        self.assertIn("/account/reset/", mail.outbox[0].body)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_does_not_disclose_an_unknown_email_address(self):
        response = self.client.post(reverse("accounts:password-reset"), {"email": "unknown@example.com"})

        self.assertRedirects(response, reverse("accounts:password-reset-done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_password_reset_token_has_a_safe_error_page(self):
        response = self.client.get(reverse("accounts:password-reset-confirm", kwargs={"uidb64": "MQ", "token": "invalid-token"}))

        self.assertContains(response, "This link is no longer valid.")

    def test_password_reset_completes_with_a_valid_token_and_cannot_be_reused(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        reset_url = reverse("accounts:password-reset-confirm", kwargs={"uidb64": uidb64, "token": token})

        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            response.url,
            {"new_password1": "a-different-secure-password-123", "new_password2": "a-different-secure-password-123"},
        )

        self.assertRedirects(response, reverse("accounts:password-reset-complete"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("a-different-secure-password-123"))
        self.assertContains(self.client.get(reset_url), "This link is no longer valid.")
