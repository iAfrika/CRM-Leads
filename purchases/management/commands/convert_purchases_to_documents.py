from django.core.management.base import BaseCommand
from django.db import transaction
from purchases.models import Purchase
from documents.models import Document

class Command(BaseCommand):
    help = 'Convert existing Purchases to Documents'

    def handle(self, *args, **options):
        # Find purchases without a corresponding document
        purchases_without_docs = Purchase.objects.exclude(document__isnull=False)
        
        self.stdout.write(f"Found {purchases_without_docs.count()} purchases to convert")
        
        converted_count = 0
        for purchase in purchases_without_docs:
            try:
                with transaction.atomic():
                    purchase.create_document()
                    converted_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to convert purchase {purchase.id}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully converted {converted_count} purchases to documents"))
