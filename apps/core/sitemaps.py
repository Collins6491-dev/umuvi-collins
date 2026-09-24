from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.portfolio.models import Project


class PortfolioSitemap(Sitemap):
    protocol = "https"
    priority = 0.7

    def items(self):
        return ["home", *Project.objects.published().only("slug", "updated_at")]

    def location(self, item):
        return reverse("portfolio:home") if item == "home" else item.get_absolute_url()

    def lastmod(self, item):
        return getattr(item, "updated_at", None)

    def priority(self, item):
        return 1.0 if item == "home" else 0.8
