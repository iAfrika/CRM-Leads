from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Set up staff users and permissions'

    def handle(self, *args, **kwargs):
        # Create Staff group
        staff_group, created = Group.objects.get_or_create(name='Staff')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Staff group'))

        # Get the Procurement user
        try:
            user = User.objects.get(username='Procurement')
            
            # Make them staff
            user.is_staff = True
            user.save()
            self.stdout.write(f'Made {user.username} a staff member')

            # Add to Staff group
            user.groups.add(staff_group)
            self.stdout.write(f'Added {user.username} to Staff group')

            self.stdout.write(self.style.SUCCESS(f'Successfully set up {user.username} as staff'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User "Procurement" not found')) 