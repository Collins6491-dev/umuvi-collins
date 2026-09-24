from django import template


register = template.Library()


@register.filter
def attr(value, name):
    """Read a named public display field from a trusted dashboard registry."""
    if str(name).startswith("_"):
        return ""
    return getattr(value, name, "")
