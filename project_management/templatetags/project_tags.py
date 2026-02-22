from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value
        
@register.filter
def percentage(value, arg):
    """Calculate percentage of value relative to arg."""
    try:
        return (float(value) / float(arg)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0