from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using the specified key.
    """
    return dictionary.get(key, '')

@register.filter
def get_field_value(obj, field_name):
    """
    Get value from either a direct field or a JSONField.
    """
    field_key = field_name.lower().replace(' ', '_').replace('.', '')
    direct_value = getattr(obj, field_key, None)
    if direct_value not in [None, '']:
        return direct_value
    return obj.data.get(field_name, '')