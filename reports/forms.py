from django import forms
from .models import (
    Report, ReportConfiguration, ReportSchedule, ReportSettings
)
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ReportConfigurationForm(forms.ModelForm):
    """
    Form for creating and updating report configurations.
    """
    name = forms.CharField(max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = ReportConfiguration
        fields = [
            'report_type', 'time_range', 'chart_type', 'filters',
            'date_field', 'group_by', 'aggregate_function', 'custom_colors'
        ]
        widgets = {
            'filters': forms.HiddenInput(),
            'custom_colors': forms.HiddenInput(),
        }
    
    def clean_filters(self):
        filters = self.cleaned_data.get('filters')
        if isinstance(filters, str):
            import json
            try:
                filters = json.loads(filters)
            except:
                filters = {}
        return filters or {}
    
    def clean_custom_colors(self):
        custom_colors = self.cleaned_data.get('custom_colors')
        if isinstance(custom_colors, str):
            import json
            try:
                custom_colors = json.loads(custom_colors)
            except:
                custom_colors = {}
        return custom_colors or {}


class ReportScheduleForm(forms.ModelForm):
    """
    Form for scheduling reports.
    """
    report = forms.ModelChoiceField(queryset=Report.objects.none())
    
    class Meta:
        model = ReportSchedule
        fields = [
            'report', 'frequency', 'day_of_week', 'day_of_month', 
            'time_of_day', 'recipients', 'subject', 'message', 'format'
        ]
        widgets = {
            'time_of_day': forms.TimeInput(attrs={'type': 'time'}),
            'message': forms.Textarea(attrs={'rows': 3}),
            'recipients': forms.TextInput(attrs={'placeholder': 'email1@example.com, email2@example.com'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['report'].queryset = Report.objects.filter(
                models.Q(created_by=user) | models.Q(shared_with=user)
            ).distinct()
        
        # Show/hide fields based on frequency
        if self.instance.pk and self.instance.frequency:
            if self.instance.frequency != 'WEEKLY':
                self.fields['day_of_week'].widget = forms.HiddenInput()
            if self.instance.frequency not in ['MONTHLY', 'QUARTERLY']:
                self.fields['day_of_month'].widget = forms.HiddenInput()


class ReportSettingsForm(forms.ModelForm):
    """
    Form for updating report settings.
    """
    class Meta:
        model = ReportSettings
        fields = [
            'default_time_range', 'default_chart_type', 'reports_per_page',
            'enable_caching', 'cache_timeout',
            'color_scheme', 'chart_font', 'chart_title_size', 'chart_label_size',
            'show_grid_lines', 'show_legends', 'legend_position',
            'default_report_access', 'allow_report_sharing'
        ]
        widgets = {
            'chart_title_size': forms.NumberInput(attrs={'min': 12, 'max': 24}),
            'chart_label_size': forms.NumberInput(attrs={'min': 10, 'max': 18}),
            'cache_timeout': forms.NumberInput(attrs={'min': 60, 'max': 86400}),
            'reports_per_page': forms.NumberInput(attrs={'min': 5, 'max': 50}),
        }
