from django import template
import os

register = template.Library()

@register.filter
def filename(value):
    """
    Returns the filename from a path.
    Usage: {{ file.name|filename }}
    """
    return os.path.basename(value)

@register.filter
def endswith(value, arg):
    """
    Checks if a value ends with a specific string.
    Usage: {% if file.name|endswith:".pdf" %}
    """
    return value.endswith(arg) 