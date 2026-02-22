from django.core.management.base import BaseCommand
from django.db import transaction
from expenses.models import Expense
from documents.models import Document

class Command(BaseCommand):
    help = 'Convert existing Expenses to Documents'

    def handle(self, *args, **options):
        # Find expenses without a corresponding document
        expenses_without_docs = Expense.objects.exclude(document__isnull=False)
        
        self.stdout.write(f"Found {expenses_without_docs.count()} expenses to convert")
        
        converted_count = 0
        for expense in expenses_without_docs:
            try:
                with transaction.atomic():
                    expense.create_document()
                    converted_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to convert expense {expense.id}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully converted {converted_count} expenses to documents"))
