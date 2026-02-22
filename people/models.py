from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    telegram_username = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    role = models.ManyToManyField(Role, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    registered_by_id = models.IntegerField(null=True, blank=True)  # Store user ID instead of ForeignKey  

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class ContactHistory(models.Model):
    CONTACT_TYPES = [
        ('email', 'Email'),
        ('telegram', 'Telegram'),
    ]
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='contact_history')
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    sent_by_id = models.IntegerField(null=True, blank=True)  # Store user ID instead of ForeignKey

    def __str__(self):
        return f"{self.person.full_name} - {self.get_contact_type_display()}"
    
    class Meta:
        ordering = ['-date_sent']   
    

