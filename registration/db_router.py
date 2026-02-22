"""
Database router for company-specific database isolation
Each company gets its own database
"""
from django.conf import settings


class CompanyDatabaseRouter:
    """
    A router to control database operations for company-specific models
    """
    
    # Models that should be in the default (shared) database
    SHARED_MODELS = [
        'auth',
        'contenttypes',
        'sessions',
        'admin',
        'registration.company',
        'registration.companyuser',
        'registration.companybankaccount',
        'registration.appmodule',
        'registration.companyapp',
        'registration.subscriptionplan',
        'registration.paymentmethod',
        'registration.subscription',
        'registration.paymenttransaction',
        'authentication.user',
        'authentication.profile',
        'authentication.group',
        'authentication.permission',
    ]
    
    def db_for_read(self, model, **hints):
        """
        Attempts to read from company-specific database if available
        """
        # Get the company database from thread local storage
        company_db = getattr(settings, 'COMPANY_DATABASE', None)
        
        model_label = f"{model._meta.app_label}.{model._meta.model_name}"
        
        # Check if model should be in shared database
        if model._meta.app_label in [label.split('.')[0] for label in self.SHARED_MODELS]:
            if model_label in self.SHARED_MODELS or model._meta.app_label in ['auth', 'contenttypes', 'sessions', 'admin']:
                return 'default'
        
        # If company database is set, use it for company-specific data
        if company_db and company_db != 'default':
            return company_db
        
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Attempts to write to company-specific database if available
        """
        return self.db_for_read(model, **hints)
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database
        """
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure shared models only migrate to default database
        Company databases get all non-shared models
        """
        if db == 'default':
            return True
        
        # For company databases, allow all migrations except shared models
        if model_name:
            model_label = f"{app_label}.{model_name}"
            if model_label in self.SHARED_MODELS or app_label in ['auth', 'contenttypes', 'sessions', 'admin']:
                return False
        
        return True
