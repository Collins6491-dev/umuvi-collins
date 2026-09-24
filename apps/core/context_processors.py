from django.conf import settings


def site_context(request):
    # Imports here prevent app-loading cycles during Django initialization.
    from apps.core.models import SectionConfiguration, SiteSettings
    from apps.portfolio.models import Experience, Profile, Service, SocialLink

    site_settings = SiteSettings.objects.order_by("id").first()
    profile = Profile.objects.order_by("id").first()
    social_links = list(SocialLink.objects.filter(is_visible=True))
    configured_sections = {item.section: item.is_visible for item in SectionConfiguration.objects.all()}
    visible_sections = {
        choice: configured_sections.get(choice, True) for choice, _ in SectionConfiguration.Section.choices
    }
    footer_navigation = [{"label": "Home", "fragment": ""}]
    if visible_sections["about"] and profile and profile.about_body:
        footer_navigation.append({"label": "About", "fragment": "about"})
    if visible_sections["projects"]:
        footer_navigation.append({"label": "Projects", "fragment": "projects"})
    if visible_sections["experience"] and Experience.objects.exists():
        footer_navigation.append({"label": "Experience", "fragment": "experience"})
    if visible_sections["contact"]:
        footer_navigation.append({"label": "Contact", "fragment": "contact"})
    schema_data = None
    if profile:
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": profile.full_name,
            "jobTitle": profile.professional_title,
            "url": (site_settings.site_url if site_settings and site_settings.site_url else settings.SITE_URL),
            "sameAs": [social.url for social in social_links],
        }

    # Unsaved defaults keep public and error templates usable before an administrator
    # has entered the first real record. They are presentation fallbacks, never data.
    return {
        "site_settings": site_settings or SiteSettings(site_name="Portfolio"),
        "global_profile": profile or Profile(full_name="Portfolio"),
        "schema_data": schema_data,
        "site_url": settings.SITE_URL,
        "social_links": social_links,
        "footer_navigation": footer_navigation,
        "footer_services": Service.objects.filter(is_visible=True),
    }
