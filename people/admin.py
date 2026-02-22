from django.contrib import admin
from .models import Person, Role, ContactHistory

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'telegram_username', 'date_registered')
    list_filter = ('role', 'date_registered')
    search_fields = ('first_name', 'last_name', 'email', 'telegram_username')
    filter_horizontal = ('role',)
    date_hierarchy = 'date_registered'

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(ContactHistory)
class ContactHistoryAdmin(admin.ModelAdmin):
    list_display = ('person', 'contact_type', 'subject', 'date_sent', 'sent_by_id')
    list_filter = ('contact_type', 'date_sent')
    search_fields = ('person__first_name', 'person__last_name', 'subject', 'message')
    date_hierarchy = 'date_sent'