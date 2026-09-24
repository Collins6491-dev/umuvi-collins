from __future__ import annotations

import hashlib

from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ContactForm


def _fingerprint(request) -> str:
    # REMOTE_ADDR is deliberately used instead of untrusted forwarding headers.
    return hashlib.sha256(request.META.get("REMOTE_ADDR", "").encode()).hexdigest()


@require_POST
def submit_contact(request):
    fingerprint = _fingerprint(request)
    rate_key = f"contact-form:{fingerprint}"
    if not cache.add(rate_key, 1, timeout=3600):
        return HttpResponse("Please wait before sending another message.", status=429)

    form = ContactForm(request.POST)
    if form.is_valid():
        submission = form.save(commit=False)
        submission.source_fingerprint = fingerprint
        submission.save()
        messages.success(request, "Thanks — your message has been received.")
    else:
        messages.error(request, "Please correct the form and try again.")
    return redirect(f"{reverse('portfolio:home')}#contact")
