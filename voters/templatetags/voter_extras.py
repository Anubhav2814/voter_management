from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary
    """
    return dictionary.get(key, '')


@register.filter
def get_field_value(obj, field_name):
    """
    Get value from either direct field or data JSONField
    """
    # Try to get from model field first
    field_key = field_name.lower().replace(' ', '_').replace('.', '')
    direct_value = getattr(obj, field_key, None)
    if direct_value not in [None, '']:
        return direct_value

    # Fall back to data field
    return obj.data.get(field_name, '')