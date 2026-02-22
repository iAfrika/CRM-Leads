from django import template
from django.db.models import Sum
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def currency(value):
    """Format a number as currency."""
    if value is None:
        return ''
    return "${:,.2f}".format(value)

@register.filter
def sum_amount(queryset):
    """Calculate the sum of amounts for a queryset of expenses."""
    result = queryset.aggregate(Sum('amount'))['amount__sum']
    return result or 0

@register.filter
def kes_format(value):
    """
    Format a number as Kenyan Shillings with comma as thousands separator.
    Example: 1234.56 -> KES 1,234.56
    """
    if value is None:
        return "KES 0.00"
    
    # Format with commas and 2 decimal places
    formatted_value = floatformat(value, 2)
    
    # Add commas for thousands
    parts = formatted_value.split('.')
    integer_part = parts[0]
    
    # Handle negative numbers
    sign = ""
    if integer_part.startswith('-'):
        sign = "-"
        integer_part = integer_part[1:]
    
    # Add commas
    result = ""
    for i, char in enumerate(reversed(integer_part)):
        if i > 0 and i % 3 == 0:
            result = ',' + result
        result = char + result
    
    # Reconstruct with decimal part
    if len(parts) > 1:
        result = f"{sign}{result}.{parts[1]}"
    else:
        result = f"{sign}{result}"
    
    return f"KES {result}"

@register.filter
def comma_format(value):
    """
    Format a number with comma as thousands separator.
    Example: 1234 -> 1,234
    """
    if value is None:
        return "0"
    
    # Convert to string and handle decimals
    str_value = str(value)
    parts = str_value.split('.')
    integer_part = parts[0]
    
    # Handle negative numbers
    sign = ""
    if integer_part.startswith('-'):
        sign = "-"
        integer_part = integer_part[1:]
    
    # Add commas
    result = ""
    for i, char in enumerate(reversed(integer_part)):
        if i > 0 and i % 3 == 0:
            result = ',' + result
        result = char + result
    
    # Reconstruct with decimal part
    if len(parts) > 1:
        result = f"{sign}{result}.{parts[1]}"
    else:
        result = f"{sign}{result}"
    
    return result 