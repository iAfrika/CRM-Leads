"""
Management command to populate default app modules
"""
from django.core.management.base import BaseCommand
from registration.models import AppModule


class Command(BaseCommand):
    help = 'Populate default app modules in the system'

    def handle(self, *args, **options):
        app_modules = [
            {
                'name': 'dashboard',
                'display_name': 'Dashboard',
                'description': 'Main dashboard with analytics and overview',
                'icon': 'fas fa-tachometer-alt',
                'order': 1,
                'requires_subscription': False,
            },
            {
                'name': 'clients',
                'display_name': 'Clients Management',
                'description': 'Manage your client database and relationships',
                'icon': 'fas fa-users',
                'order': 2,
                'requires_subscription': False,
            },
            {
                'name': 'leads',
                'display_name': 'Leads Management',
                'description': 'Track and convert leads into customers',
                'icon': 'fas fa-user-plus',
                'order': 3,
                'requires_subscription': False,
            },
            {
                'name': 'sales',
                'display_name': 'Sales Management',
                'description': 'Manage sales, quotes, and invoices',
                'icon': 'fas fa-dollar-sign',
                'order': 4,
                'requires_subscription': False,
            },
            {
                'name': 'projects',
                'display_name': 'Project Management',
                'description': 'Track projects, tasks, and milestones',
                'icon': 'fas fa-project-diagram',
                'order': 5,
                'requires_subscription': True,
            },
            {
                'name': 'documents',
                'display_name': 'Document Management',
                'description': 'Store and manage your business documents',
                'icon': 'fas fa-file-alt',
                'order': 6,
                'requires_subscription': False,
            },
            {
                'name': 'expenses',
                'display_name': 'Expense Tracking',
                'description': 'Track and categorize business expenses',
                'icon': 'fas fa-receipt',
                'order': 7,
                'requires_subscription': True,
            },
            {
                'name': 'purchases',
                'display_name': 'Purchase Management',
                'description': 'Manage purchase orders and vendor relationships',
                'icon': 'fas fa-shopping-cart',
                'order': 8,
                'requires_subscription': True,
            },
            {
                'name': 'banking',
                'display_name': 'Banking & Finance',
                'description': 'Track bank accounts and transactions',
                'icon': 'fas fa-university',
                'order': 9,
                'requires_subscription': True,
            },
            {
                'name': 'reports',
                'display_name': 'Reports & Analytics',
                'description': 'Generate detailed business reports and insights',
                'icon': 'fas fa-chart-bar',
                'order': 10,
                'requires_subscription': True,
            },
            {
                'name': 'people',
                'display_name': 'People Management',
                'description': 'Manage employees and contacts',
                'icon': 'fas fa-address-book',
                'order': 11,
                'requires_subscription': True,
            },
            {
                'name': 'communication',
                'display_name': 'Communication',
                'description': 'Manage emails, calls, and meetings',
                'icon': 'fas fa-comments',
                'order': 12,
                'requires_subscription': False,
            },
        ]

        created_count = 0
        updated_count = 0

        for module_data in app_modules:
            module, created = AppModule.objects.update_or_create(
                name=module_data['name'],
                defaults={
                    'display_name': module_data['display_name'],
                    'description': module_data['description'],
                    'icon': module_data['icon'],
                    'order': module_data['order'],
                    'requires_subscription': module_data['requires_subscription'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {module.display_name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {module.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated {created_count} new app modules and updated {updated_count} existing ones.'
            )
        )
