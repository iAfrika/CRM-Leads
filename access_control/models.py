from django.db import models
from django.contrib.auth.models import User
from django.apps import apps

class View(models.Model):
    """
    Model to store views that can be accessed.
    Each entry represents a view in the system.
    """
    name = models.CharField(max_length=254)
    app_name = models.CharField(max_length=100)
    view_name = models.CharField(max_length=100)
    url_pattern = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('app_name', 'view_name')
        ordering = ['app_name', 'view_name']
        verbose_name = 'View'
        verbose_name_plural = 'Views'

    def __str__(self):
        return f"{self.app_name} - {self.name}"

    @classmethod
    def get_available_apps(cls):
        """Return a list of all installed apps that can have permissions"""
        excluded_apps = [
            'admin', 'auth', 'contenttypes', 'sessions', 
            'messages', 'staticfiles', 'rest_framework'
        ]
        return [
            app for app in apps.get_app_configs() 
            if app.name not in excluded_apps
        ]

class Permission(models.Model):
    """
    Model to store user permissions.
    Links users to views they can access.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='access_control_permissions'
    )
    view = models.ForeignKey(
        View,
        on_delete=models.CASCADE,
        related_name='user_permissions'
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='access_control_granted_permissions'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'view')
        ordering = ['user', 'view']
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

    def __str__(self):
        return f"{self.user.username} - {self.view.name}" 