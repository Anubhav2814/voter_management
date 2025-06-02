from django import template

register = template.Library()

@register.filter
def split_tags(value):
    """Split comma-separated tags into a list"""
    if value:
        return [tag.strip() for tag in value.split(',') if tag.strip()]
    return []
