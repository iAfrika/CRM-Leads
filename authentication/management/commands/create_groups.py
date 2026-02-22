from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

class Command(BaseCommand):
    help = 'Create default user groups and assign staff users'

    def handle(self, *args, **kwargs):
        # Create Staff group if it doesn't exist
        staff_group, created = Group.objects.get_or_create(name='Staff')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Staff group'))
        
        # Get all non-superuser staff users
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        
        # Add users to Staff group
        for user in staff_users:
            user.groups.add(staff_group)
            self.stdout.write(f'Added {user.username} to Staff group')

        self.stdout.write(self.style.SUCCESS('Successfully set up staff users')) 