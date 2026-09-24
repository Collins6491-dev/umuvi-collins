from django.contrib import admin

from .models import SectionConfiguration, SiteSettings

admin.site.register([SiteSettings, SectionConfiguration])
