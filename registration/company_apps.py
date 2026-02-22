"""
Company App Association Module
Manages which apps/modules are enabled for each company
"""
from django.db import models
from django.conf import settings
from .models import Company


class AppModule(models.Model):
    """
    Represents an available application module in the system
    """
    APP_CHOICES = [
        ('clients', 'Clients Management'),
        ('leads', 'Leads Management'),
        ('sales', 'Sales Management'),
        ('projects', 'Project Management'),
        ('documents', 'Document Management'),
        ('expenses', 'Expense Tracking'),
        ('purchases', 'Purchase Management'),
        ('banking', 'Banking & Finance'),
        ('reports', 'Reports & Analytics'),
        ('people', 'People Management'),
        ('communication', 'Communication'),
        ('dashboard', 'Dashboard'),
    ]
    
    name = models.CharField(max_length=50, unique=True, choices=APP_CHOICES)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-puzzle-piece')
    is_active = models.BooleanField(default=True)
    requires_subscription = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'display_name']
        verbose_name = 'App Module'
        verbose_name_plural = 'App Modules'
    
    def __str__(self):
        return self.display_name


class CompanyApp(models.Model):
    """
    Many-to-many relationship between companies and app modules
    Tracks which apps are enabled for each company
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='enabled_apps')
    app_module = models.ForeignKey(AppModule, on_delete=models.CASCADE, related_name='companies')
    is_enabled = models.BooleanField(default=True)
    enabled_at = models.DateTimeField(auto_now_add=True)
    enabled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='enabled_company_apps'
    )
    settings = models.JSONField(default=dict, blank=True)  # For app-specific settings
    
    class Meta:
        unique_together = ('company', 'app_module')
        verbose_name = 'Company App'
        verbose_name_plural = 'Company Apps'
        ordering = ['app_module__order', 'app_module__display_name']
    
    def __str__(self):
        return f"{self.company.name} - {self.app_module.display_name}"


def get_company_enabled_apps(company):
    """
    Get all enabled apps for a company
    Returns a list of app names
    """
    return list(
        CompanyApp.objects.filter(
            company=company,
            is_enabled=True,
            app_module__is_active=True
        ).values_list('app_module__name', flat=True)
    )


def is_app_enabled_for_company(company, app_name):
    """
    Check if a specific app is enabled for a company
    """
    return CompanyApp.objects.filter(
        company=company,
        app_module__name=app_name,
        is_enabled=True,
        app_module__is_active=True
    ).exists()


def enable_default_apps_for_company(company, user=None):
    """
    Enable default apps for a newly registered company
    """
    default_apps = ['dashboard', 'clients', 'leads', 'sales', 'documents']
    
    for app_name in default_apps:
        try:
            app_module = AppModule.objects.get(name=app_name)
            CompanyApp.objects.get_or_create(
                company=company,
                app_module=app_module,
                defaults={
                    'is_enabled': True,
                    'enabled_by': user
                }
            )
        except AppModule.DoesNotExist:
            continue
