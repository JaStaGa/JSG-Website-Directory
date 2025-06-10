from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def querystring(filters, **kwargs):
    params = filters.copy()
    params.update(kwargs)
    return urlencode({k: v for k, v in params.items() if v})

@register.filter
def trim(value):
    if isinstance(value, str):
        return value.strip()
    return value
