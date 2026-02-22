from django import template
from django.db.models import Sum

register = template.Library()

@register.filter
def sum_amount(queryset):
    """Calculate the sum of amounts for a queryset of expenses."""
    result = queryset.aggregate(Sum('amount'))['amount__sum']
    return result or 0 