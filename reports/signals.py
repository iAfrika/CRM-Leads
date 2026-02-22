from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Report, ReportConfiguration, ReportSettings

User = get_user_model()


@receiver(post_save, sender=Report)
def create_report_configuration(sender, instance, created, **kwargs):
    """
    Create a ReportConfiguration when a Report is created.
    """
    if created and not hasattr(instance, 'configuration'):
        ReportConfiguration.objects.create(
            report=instance,
            report_type='CUSTOM',
            time_range='MONTHLY',
            chart_type='BAR'
        )


@receiver(post_save, sender=User)
def create_user_report_settings(sender, instance, created, **kwargs):
    """
    Create ReportSettings when a User is created.
    """
    if created:
        ReportSettings.objects.create(user=instance)
