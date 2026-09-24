from django.test import TestCase
from django.urls import reverse


class CoreResponseTests(TestCase):
    def test_home_sends_a_restrictive_content_security_policy(self):
        response = self.client.get(reverse("portfolio:home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertIn("script-src 'self' 'nonce-", response.headers["Content-Security-Policy"])
        self.assertNotIn("unsafe-inline", response.headers["Content-Security-Policy"])

    def test_public_navigation_has_accessible_mobile_menu_controls(self):
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, 'aria-controls="primary-menu"')
        self.assertContains(response, 'aria-label="Open navigation"')
        self.assertContains(response, "data-nav-overlay")

    def test_robots_disallows_private_routes_and_exposes_sitemap(self):
        response = self.client.get(reverse("robots-txt"))
        self.assertContains(response, "Disallow: /dashboard/")
        self.assertContains(response, "Sitemap:")
