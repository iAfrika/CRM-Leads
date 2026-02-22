from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import Product

@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    """Handle pre-save operations for Product model."""
    pass

@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    """Handle post-save operations for Product model."""
    pass

@receiver(pre_delete, sender=Product)
def product_pre_delete(sender, instance, **kwargs):
    """Handle pre-delete operations for Product model."""
    pass

@receiver(post_delete, sender=Product)
def product_post_delete(sender, instance, **kwargs):
    """Handle post-delete operations for Product model."""
    pass