from django.core.management.base import BaseCommand
from people.models import Person
from django.db.models import Count

class Command(BaseCommand):
    help = 'Fixes duplicate phone numbers and telegram usernames'

    def handle(self, *args, **options):
        self.stdout.write('Fixing duplicate phone numbers...')
        self._fix_duplicates('phone')
        
        self.stdout.write('Fixing duplicate telegram usernames...')
        self._fix_duplicates('telegram_username')
        
        self.stdout.write(self.style.SUCCESS('Successfully fixed all duplicates'))

    def _fix_duplicates(self, field_name):
        # Find duplicates
        filter_kwargs = {f"{field_name}__isnull": False}
        duplicates = (
            Person.objects.filter(**filter_kwargs)
            .values(field_name)
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )
        
        for dup in duplicates:
            value = dup[field_name]
            self.stdout.write(f"Found duplicate {field_name}: {value}")
            
            # Get all persons with this value
            filter_kwargs = {field_name: value}
            persons = Person.objects.filter(**filter_kwargs).order_by('id')
            
            # Keep the first one (oldest record) unchanged
            self.stdout.write(f"  Keeping {field_name} for {persons[0]}")
            
            # Add a suffix to others
            for i, person in enumerate(persons[1:], 1):
                new_value = f"{value}-{i}"
                self.stdout.write(f"  Changing {field_name} for {person} to {new_value}")
                
                # Update the field
                setattr(person, field_name, new_value)
                person.save(update_fields=[field_name]) 