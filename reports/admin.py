from django.contrib import admin
from .models import (
    Report, ReportConfiguration, ReportSchedule, 
    ReportDelivery, ReportSettings
)


class ReportConfigurationInline(admin.StackedInline):
    model = ReportConfiguration
    can_delete = False
    verbose_name_plural = 'Configuration'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'created_by__username')
    inlines = [ReportConfigurationInline]


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ('report', 'frequency', 'is_active', 'next_run', 'last_run')
    list_filter = ('frequency', 'is_active', 'created_at')
    search_fields = ('report__name', 'subject')


@admin.register(ReportDelivery)
class ReportDeliveryAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'status', 'sent_at', 'format')
    list_filter = ('status', 'sent_at', 'format')
    search_fields = ('schedule__report__name', 'recipients', 'subject')


@admin.register(ReportSettings)
class ReportSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_time_range', 'default_chart_type')
    list_filter = ('default_time_range', 'default_chart_type', 'color_scheme')
    search_fields = ('user__username',)
