from django.contrib import admin
from .models import Lead, LeadActivity

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'contact_person', 'email', 'status', 'priority', 'assigned_to']
    list_filter = ['status', 'priority', 'source', 'created_at']
    search_fields = ['title', 'company_name', 'contact_person', 'email']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company_name', 'contact_person', 'email', 'phone', 'website')
        }),
        ('Lead Details', {
            'fields': ('description', 'requirements', 'estimated_value', 'status', 'source', 'priority')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'tags')
        }),
        ('Notes', {
            'fields': ('notes_text',)
        }),
        ('Dates', {
            'fields': ('next_follow_up', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ['lead', 'activity_type', 'created_at', 'created_by_id', 'is_completed']
    list_filter = ['activity_type', 'is_completed', 'created_at']
    search_fields = ['lead__company_name', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    fieldsets = (
        ('Activity Information', {
            'fields': ('lead', 'activity_type', 'description')
        }),
        ('Dates and Status', {
            'fields': ('created_at', 'due_date', 'is_completed', 'completed_at')
        }),
        ('User Information', {
            'fields': ('created_by_id',)
        }),
    )
