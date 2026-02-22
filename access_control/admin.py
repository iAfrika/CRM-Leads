from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import View, Permission

class PermissionInline(admin.TabularInline):
    """Inline admin for permissions"""
    model = Permission
    extra = 1
    raw_id_fields = ('view', 'granted_by')
    autocomplete_fields = ('view',)
    fk_name = 'user'  # Specify which foreign key to use for the inline

class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin with permissions inline"""
    inlines = BaseUserAdmin.inlines + (PermissionInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(View)
class ViewAdmin(admin.ModelAdmin):
    """Admin interface for views"""
    list_display = ('name', 'app_name', 'view_name', 'url_pattern', 'created_at')
    list_filter = ('app_name',)
    search_fields = ('name', 'app_name', 'view_name', 'url_pattern')
    ordering = ('app_name', 'view_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'app_name', 'view_name', 'url_pattern')
        }),
        ('Additional Information', {
            'fields': ('description', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin interface for permissions"""
    list_display = ('user', 'view', 'granted_by', 'granted_at', 'is_active')
    list_filter = ('is_active', 'granted_at', 'view__app_name')
    search_fields = ('user__username', 'view__name', 'notes')
    raw_id_fields = ('user', 'view', 'granted_by')
    autocomplete_fields = ('view',)
    readonly_fields = ('granted_at',)
    ordering = ('-granted_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'view', 'is_active')
        }),
        ('Grant Information', {
            'fields': ('granted_by', 'granted_at', 'notes'),
            'classes': ('collapse',)
        }),
    ) 