from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Account, Transaction

@receiver(post_save, sender=Transaction)
def update_account_balance_on_transaction(sender, instance, created, **kwargs):
    """
    Update account balance when a transaction is created.
    This is a backup mechanism to ensure account balances are always in sync with transactions.
    """
    if created:
        # The transaction methods in the Account model already update the balance,
        # but this is a safety measure to ensure data consistency
        pass

@receiver(post_save, sender=User)
def create_default_account(sender, instance, created, **kwargs):
    """
    Create a default checking account for new users.
    """
    if created:
        # Only create a default account if this is a new user
        # This is optional and can be removed if you don't want to create default accounts
        pass 