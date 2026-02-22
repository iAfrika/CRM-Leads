from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('administrator', 'Administrator'),
        ('staff', 'Staff'),
    )
    
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pin = models.CharField(max_length=4, default='0000')
    avatar = models.ImageField(upload_to='profile_avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        # Ensure admin users always have administrator role
        if self.user.username.lower() == 'admin' or self.user.is_superuser:
            self.role = 'administrator'
        
        # Ensure role is standardized
        if self.role == 'admin':
            self.role = 'administrator'
            
        super(Profile, self).save(*args, **kwargs)
