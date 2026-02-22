from django.apps import AppConfig

class AccessControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'access_control'
    verbose_name = 'Access Control'

    def ready(self):
        """
        Perform any app initialization here.
        This method is called when the app is ready.
        """
        pass  # We can add signal registrations or other initialization here if needed 