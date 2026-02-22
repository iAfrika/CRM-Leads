from django.contrib import admin
from .models import Client
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    search_fields = ['name', 'email']
    list_filter = ['created_at']

class Command(BaseCommand):
    help = 'Create default user groups'

    def handle(self, *args, **kwargs):
        Group.objects.get_or_create(name='Staff')
        self.stdout.write('Successfully created Staff group')

