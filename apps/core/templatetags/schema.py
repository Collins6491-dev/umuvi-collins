import json

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def json_ld(data, nonce=""):
    """Render server-produced JSON-LD without letting editable content escape the script tag."""
    if not data:
        return ""
    encoded = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(f'<script type="application/ld+json" nonce="{nonce}">{encoded}</script>')
