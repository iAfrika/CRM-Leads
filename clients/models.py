from django.db import models
from django.urls import reverse
import uuid


# Create your models here.
class Client(models.Model):
    client_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    name = models.CharField(max_length=200)
    initials = models.CharField(max_length=10, verbose_name='Client Initials', help_text='2-5 characters', blank=True)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Client ID is now generated in the view to use company initials
        # This is a fallback in case it's not set
        if not self.client_id:
            import re
            last_client = Client.objects.order_by('-id').first()
            if last_client and last_client.client_id:
                try:
                    numbers = re.findall(r'\d+', last_client.client_id)
                    last_number = int(numbers[-1]) if numbers else 0
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            # Default format if no company context available
            self.client_id = f"CC{new_number:04d}"
            
            # Ensure uniqueness
            while Client.objects.filter(client_id=self.client_id).exists():
                new_number += 1
                self.client_id = f"CC{new_number:04d}"
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('clients:client_detail', kwargs={'pk': self.pk})

