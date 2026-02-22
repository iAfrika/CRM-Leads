from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def thousands_separator(value):
    """
    Format a number with thousands separator.
    Example: 1234567 becomes 1,234,567
    """
    try:
        if value is None:
            return '0'
        # Convert to float first to handle decimal numbers
        value = float(str(value).replace(',', ''))
        # Format with commas
        if value.is_integer():
            # If it's a whole number, don't show decimal places
            return '{:,.0f}'.format(value)
        else:
            # If it has decimal places, show them
            return '{:,.2f}'.format(value)
    except (ValueError, TypeError):
        return value