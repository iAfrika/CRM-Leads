"""
Management command to run migrations on all company databases
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from registration.models import Company
from registration.company_database import create_company_database, get_company_database_name, get_company_database_settings


class Command(BaseCommand):
    help = 'Run migrations on all company databases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company-id',
            type=int,
            help='Run migrations for a specific company by ID',
        )

    def handle(self, *args, **options):
        company_id = options.get('company_id')
        
        if company_id:
            # Run for specific company
            try:
                company = Company.objects.get(id=company_id)
                companies = [company]
            except Company.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Company with ID {company_id} not found'))
                return
        else:
            # Run for all companies
            companies = Company.objects.all()
        
        if not companies:
            self.stdout.write(self.style.WARNING('No companies found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Processing {len(companies)} company database(s)...'))
        
        success_count = 0
        failed_count = 0
        
        for company in companies:
            self.stdout.write(f'\n{"-" * 60}')
            self.stdout.write(f'Processing: {company.name} (ID: {company.id})')
            
            db_name = get_company_database_name(company)
            db_settings = get_company_database_settings(company)
            
            self.stdout.write(f'Database: {db_name}')
            self.stdout.write(f'Path: {db_settings["NAME"]}')
            
            # Ensure database is in settings
            if db_name not in settings.DATABASES:
                settings.DATABASES[db_name] = db_settings
                self.stdout.write(self.style.WARNING(f'Added {db_name} to settings.DATABASES'))
            
            # Run migrations
            result = create_company_database(company)
            
            if result:
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Migrations completed for {company.name}'))
            else:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f'✗ Migrations failed for {company.name}'))
        
        self.stdout.write(f'\n{"-" * 60}')
        self.stdout.write(self.style.SUCCESS(f'\nSummary:'))
        self.stdout.write(self.style.SUCCESS(f'  Success: {success_count}'))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'  Failed: {failed_count}'))
        self.stdout.write(f'  Total: {len(companies)}')
