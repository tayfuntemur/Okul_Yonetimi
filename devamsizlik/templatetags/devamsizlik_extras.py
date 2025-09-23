from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Dictionary'den key ile değer almak için"""
    return dictionary.get(key)