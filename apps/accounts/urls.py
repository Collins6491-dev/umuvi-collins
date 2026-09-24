from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .views import DashboardLogoutView, ThrottledLoginView


app_name = "accounts"

urlpatterns = [
    path("login/", ThrottledLoginView.as_view(), name="login"),
    path("logout/", DashboardLogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.txt",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password-reset-done"),
            # Use the canonical, environment-controlled URL rather than an
            # incoming proxy/localhost Host header in the email link.
            extra_email_context={"site_url": settings.SITE_URL},
        ),
        name="password-reset",
    ),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password-reset-done"),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password-reset-complete"),
        ),
        name="password-reset-confirm",
    ),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password-reset-complete"),
]
