from django.test import Client, TestCase
from django.urls import reverse

from .models import ContactSubmission


class ContactSecurityTests(TestCase):
    payload = {"name": "Visitor", "email": "visitor@example.com", "subject": "Hello", "message": "A concise message."}

    def test_contact_endpoint_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("contact:submit"), self.payload)
        self.assertEqual(response.status_code, 403)

    def test_contact_message_is_saved_and_rate_limited(self):
        response = self.client.post(reverse("contact:submit"), self.payload)
        self.assertRedirects(response, reverse("portfolio:home") + "#contact")
        self.assertEqual(ContactSubmission.objects.count(), 1)
        response = self.client.post(reverse("contact:submit"), self.payload)
        self.assertEqual(response.status_code, 429)
