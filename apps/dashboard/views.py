from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from apps.contact.models import ContactSubmission
from apps.core.models import SectionConfiguration, SiteSettings
from apps.portfolio.models import Profile, Project

from .forms import DashboardModelForm
from .mixins import DashboardAccessMixin
from .registry import BY_KEY, SPECS, ContentSpec


class DashboardContextMixin(DashboardAccessMixin):
    """Provides a permission-filtered navigation list to all custom CMS screens."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["content_specs"] = [
            spec for spec in SPECS if user.has_perm(f"{spec.model._meta.app_label}.view_{spec.model._meta.model_name}")
        ]
        return context


class OverviewView(DashboardContextMixin, TemplateView):
    template_name = "dashboard/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        counters = []
        for spec in SPECS:
            permission = f"{spec.model._meta.app_label}.view_{spec.model._meta.model_name}"
            if user.has_perm(permission):
                counters.append({"label": spec.label, "count": spec.model.objects.count(), "key": spec.key})
        context.update(
            {
                "counters": counters,
                "published_projects": Project.objects.published().count(),
                "new_messages": ContactSubmission.objects.filter(status=ContactSubmission.Status.NEW).count()
                if user.has_perm("contact.view_contactsubmission")
                else None,
            }
        )
        return context


class ContentMixin(DashboardContextMixin):
    action = "view"

    @cached_property
    def spec(self) -> ContentSpec:
        try:
            return BY_KEY[self.kwargs["key"]]
        except KeyError as exc:
            raise Http404("Content type not found.") from exc

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied("Dashboard access is restricted.")
        permission = f"{self.spec.model._meta.app_label}.{self.action}_{self.spec.model._meta.model_name}"
        if not request.user.has_perm(permission):
            raise PermissionDenied("You do not have permission to perform this action.")
        return super(DashboardAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["spec"] = self.spec
        context["can_create"] = self.spec.allow_create and self.request.user.has_perm(
            f"{self.spec.model._meta.app_label}.add_{self.spec.model._meta.model_name}"
        )
        context["can_delete"] = self.spec.allow_delete and self.request.user.has_perm(
            f"{self.spec.model._meta.app_label}.delete_{self.spec.model._meta.model_name}"
        )
        return context


class ContentListView(ContentMixin, ListView):
    template_name = "dashboard/content_list.html"
    context_object_name = "objects"
    paginate_by = 20
    action = "view"

    def get_queryset(self):
        queryset = self.spec.model.objects.all()
        if self.spec.model is Project:
            return queryset.select_related("category").prefetch_related("technologies")
        return queryset


class ContentFormMixin(ContentMixin):
    template_name = "dashboard/content_form.html"

    def get_form_class(self):
        return modelform_factory(self.spec.model, form=DashboardModelForm, fields=self.spec.fields)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("dashboard:content-list", kwargs={"key": self.spec.key})

    def form_valid(self, form):
        messages.success(self.request, f"{self.spec.label.rstrip('s')} saved.")
        return super().form_valid(form)


class ContentCreateView(ContentFormMixin, CreateView):
    action = "add"

    def dispatch(self, request, *args, **kwargs):
        if not self.spec.allow_create:
            raise Http404("This content cannot be created here.")
        return super().dispatch(request, *args, **kwargs)


class ContentUpdateView(ContentFormMixin, UpdateView):
    action = "change"

    def get_queryset(self):
        return self.spec.model.objects.all()


class ContentDeleteView(ContentMixin, DeleteView):
    template_name = "dashboard/content_confirm_delete.html"
    action = "delete"

    def dispatch(self, request, *args, **kwargs):
        if not self.spec.allow_delete:
            raise Http404("This content cannot be deleted here.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.spec.model.objects.all()

    def get_success_url(self):
        return reverse("dashboard:content-list", kwargs={"key": self.spec.key})

    def form_valid(self, form):
        messages.success(self.request, f"{self.spec.label.rstrip('s')} deleted.")
        return super().form_valid(form)


class SingletonFormMixin(DashboardContextMixin):
    template_name = "dashboard/singleton_form.html"
    model = None
    fields: tuple[str, ...] = ()
    permission = ""
    context_title = ""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff or not request.user.has_perm(self.permission):
            raise PermissionDenied("You do not have permission to manage this content.")
        return super(DashboardAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.model.objects.order_by("id").first()

    def get_form_class(self):
        return modelform_factory(self.model, form=DashboardModelForm, fields=self.fields)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = self.context_title
        return context

    def get_success_url(self):
        return reverse("dashboard:overview")

    def form_valid(self, form):
        messages.success(self.request, "Changes saved.")
        return super().form_valid(form)


class ProfileView(SingletonFormMixin, UpdateView):
    model = Profile
    fields = (
        "full_name",
        "professional_title",
        "hero_eyebrow",
        "hero_statement",
        "hero_supporting_text",
        "about_heading",
        "about_body",
        "profile_image",
        "resume",
    )
    permission = "portfolio.manage_profile"
    context_title = "Profile and hero"

    def get(self, request, *args, **kwargs):
        if not self.get_object():
            return redirect("dashboard:profile-create")
        return super().get(request, *args, **kwargs)


class ProfileCreateView(SingletonFormMixin, CreateView):
    model = Profile
    fields = ProfileView.fields
    permission = "portfolio.manage_profile"
    context_title = "Create profile"

    def dispatch(self, request, *args, **kwargs):
        if Profile.objects.exists():
            return redirect("dashboard:profile")
        return super().dispatch(request, *args, **kwargs)


class SettingsView(SingletonFormMixin, UpdateView):
    model = SiteSettings
    fields = ("site_name", "site_url", "default_meta_title", "default_meta_description", "og_image", "contact_email", "primary_cta_label", "secondary_cta_label")
    permission = "core.change_sitesettings"
    context_title = "Site settings"

    def get(self, request, *args, **kwargs):
        if not self.get_object():
            return redirect("dashboard:settings-create")
        return super().get(request, *args, **kwargs)


class SettingsCreateView(SingletonFormMixin, CreateView):
    model = SiteSettings
    fields = SettingsView.fields
    permission = "core.change_sitesettings"
    context_title = "Create site settings"

    def dispatch(self, request, *args, **kwargs):
        if SiteSettings.objects.exists():
            return redirect("dashboard:settings")
        if request.user.is_authenticated and not request.user.has_perm("core.add_sitesettings"):
            raise PermissionDenied("You do not have permission to create site settings.")
        return super().dispatch(request, *args, **kwargs)
