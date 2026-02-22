#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from documents.models import Document

try:
    doc = Document.objects.get(id=22)
    print(f"Document ID: {doc.id}")
    print(f"Document Type: {doc.document_type}")
    print(f"Status: {doc.status}")
    print(f"Should show status update button: {doc.document_type == 'INVOICE' and doc.status not in ['PAID', 'CANCELLED']}")
    
    # List all documents to see what we have
    print("\nAll documents:")
    for d in Document.objects.all()[:10]:
        print(f"ID: {d.id}, Type: {d.document_type}, Status: {d.status}")
        
except Document.DoesNotExist:
    print("Document with ID 22 does not exist")
    print("Available documents:")
    for d in Document.objects.all()[:10]:
        print(f"ID: {d.id}, Type: {d.document_type}, Status: {d.status}")
