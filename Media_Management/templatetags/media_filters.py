from django import template

register = template.Library()

@register.filter
def split_tags(value):
    """
    Split a comma-separated string into a list and strip whitespace
    Usage: {{ value|split_tags }}
    """
    if not value:
        return []
    return [tag.strip() for tag in value.split(',')]