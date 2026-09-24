from __future__ import annotations

import hashlib

from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.cache import cache
from django.shortcuts import render


class ThrottledLoginView(LoginView):
    """Use generic responses and per-IP/per-account limits to slow credential attacks."""

    template_name = "registration/login.html"
    authentication_form = AuthenticationForm
    max_attempts_per_account = 10
    max_attempts_per_ip = 30
    window_seconds = 60 * 60

    def _key(self, scope: str) -> str:
        value = self.request.META.get("REMOTE_ADDR", "")
        if scope == "account":
            value += ":" + self.request.POST.get("username", "").strip().lower()
        digest = hashlib.sha256(value.encode()).hexdigest()
        return f"login-attempt:{scope}:{digest}"

    def _limited(self) -> bool:
        return any(
            cache.get(self._key(scope), 0) >= maximum
            for scope, maximum in (("account", self.max_attempts_per_account), ("ip", self.max_attempts_per_ip))
        )

    def _record_failure(self) -> None:
        for scope in ("account", "ip"):
            key = self._key(scope)
            if cache.add(key, 1, self.window_seconds):
                continue
            try:
                cache.incr(key)
            except ValueError:
                cache.set(key, 1, self.window_seconds)

    def post(self, request, *args, **kwargs):
        if self._limited():
            messages.error(request, "We could not sign you in. Please wait and try again.")
            form = self.get_form_class()(request)
            return render(request, self.template_name, {"form": form}, status=429)

        response = super().post(request, *args, **kwargs)
        if 200 <= response.status_code < 300:
            self._record_failure()
        else:
            cache.delete(self._key("account"))
        return response


class DashboardLogoutView(LogoutView):
    """Keep Django's session invalidation while confirming the completed action."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, "You have been signed out.")
        return response
