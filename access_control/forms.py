from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from .models import View, Permission

class ViewForm(forms.ModelForm):
    """Form for adding or editing a View"""
    
    class Meta:
        model = View
        fields = ['name', 'app_name', 'view_name', 'url_pattern', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'app_name': _('The Django app this view belongs to.'),
            'view_name': _('The name of the view function or class.'),
            'url_pattern': _('The URL pattern that routes to this view.'),
        }

class PermissionForm(forms.ModelForm):
    """Form for adding or editing a Permission"""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_superuser=False, is_staff=False),
        label=_('User'),
        help_text=_('The user this permission is for.')
    )
    
    view = forms.ModelChoiceField(
        queryset=View.objects.all(),
        label=_('View'),
        help_text=_('The view this permission grants access to.')
    )
    
    class Meta:
        model = Permission
        fields = ['user', 'view', 'is_active', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'is_active': _('Designates whether this permission is active.'),
            'notes': _('Additional notes about this permission.'),
        } 