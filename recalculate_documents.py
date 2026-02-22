#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from documents.models import Document

def recalculate_documents():
    """Recalculate all documents based on their apply_vat field"""
    documents = Document.objects.all()
    
    print(f"Found {documents.count()} documents to recalculate")
    
    for doc in documents:
        old_tax = doc.tax_amount
        old_total = doc.total_amount
        
        # Recalculate based on apply_vat
        if doc.apply_vat:
            doc.tax_amount = doc.subtotal * (doc.tax_rate / 100)
        else:
            doc.tax_amount = 0
        
        doc.total_amount = doc.subtotal + doc.tax_amount
        
        # Only update if values changed
        if old_tax != doc.tax_amount or old_total != doc.total_amount:
            Document.objects.filter(id=doc.id).update(
                tax_amount=doc.tax_amount,
                total_amount=doc.total_amount
            )
            print(f"Updated Document {doc.id}:")
            print(f"  Subtotal: {doc.subtotal}")
            print(f"  Apply VAT: {doc.apply_vat}")
            print(f"  Tax: {old_tax} -> {doc.tax_amount}")
            print(f"  Total: {old_total} -> {doc.total_amount}")
        else:
            print(f"Document {doc.id} already correct")
    
    print("\nRecalculation complete!")

if __name__ == '__main__':
    recalculate_documents()
