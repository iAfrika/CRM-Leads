#!/usr/bin/env python
import os
import sys
import django
import sqlite3
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from registration.models import Company

# Get all companies
companies = Company.objects.all()

print("Searching for document with subtotal ~237,200...\n")

for company in companies:
    db_path = f"company_databases/{company.database_name}.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found, skipping...")
        continue
    
    print(f"\n=== Checking {company.name} ({db_path}) ===")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if documents table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents_document'")
        if not cursor.fetchone():
            print("  No documents table found")
            conn.close()
            continue
        
        # Find documents with subtotal around 237,200
        cursor.execute("""
            SELECT id, document_type, subtotal, apply_vat, tax_rate, tax_amount, total_amount
            FROM documents_document
            WHERE subtotal >= 237000 AND subtotal <= 238000
        """)
        
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                doc_id, doc_type, subtotal, apply_vat, tax_rate, tax_amount, total_amount = row
                print(f"\n  Found Document ID: {doc_id}")
                print(f"  Type: {doc_type}")
                print(f"  Subtotal: {subtotal}")
                print(f"  Apply VAT: {apply_vat}")
                print(f"  Tax Rate: {tax_rate}%")
                print(f"  Tax Amount: {tax_amount}")
                print(f"  Total: {total_amount}")
                
                # Fix if apply_vat is False but tax_amount is not 0
                if not apply_vat and tax_amount != 0:
                    print(f"  ⚠️  NEEDS FIX: apply_vat is False but tax_amount is {tax_amount}")
                    new_tax = 0
                    new_total = subtotal
                    cursor.execute("""
                        UPDATE documents_document 
                        SET tax_amount = ?, total_amount = ?
                        WHERE id = ?
                    """, (new_tax, new_total, doc_id))
                    conn.commit()
                    print(f"  ✅ FIXED: tax_amount = 0, total_amount = {new_total}")
        else:
            print("  No matching documents")
            
    except sqlite3.Error as e:
        print(f"  Error: {e}")
    finally:
        conn.close()

print("\n\nDone!")
