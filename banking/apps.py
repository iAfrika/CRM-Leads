from django.apps import AppConfig


class BankingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'banking'
    verbose_name = 'Banking Management'
    
    def ready(self):
        """
        Import signals when the app is ready.
        This is needed for any signal handlers to be registered.
        """
        import banking.signals
