#!/usr/bin/env python
"""
Script to create sample products for demonstration
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from products.models import Product, Category
from django.contrib.auth.models import User

def create_sample_data():
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Create categories
    categories_data = [
        {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
        {'name': 'Clothing', 'description': 'Apparel and fashion items'},
        {'name': 'Books', 'description': 'Books and educational materials'},
        {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        categories[cat_data['name']] = category
    
    # Create sample products
    products_data = [
        {
            'item_code': 'ELEC-001',
            'name': 'Wireless Bluetooth Headphones',
            'description': 'Premium wireless headphones with active noise cancellation, 30-hour battery life, and superior sound quality.',
            'category': categories['Electronics'],
            'buying_price': 45.00,
            'selling_price': 89.99,
            'current_stock': 25,
            'reorder_level': 10,
        },
        {
            'item_code': 'ELEC-002',
            'name': 'Smartphone Stand',
            'description': 'Adjustable aluminum smartphone stand compatible with all phone sizes.',
            'category': categories['Electronics'],
            'buying_price': 12.50,
            'selling_price': 24.99,
            'current_stock': 50,
            'reorder_level': 15,
        },
        {
            'item_code': 'CLOTH-001',
            'name': 'Cotton T-Shirt',
            'description': 'Premium 100% cotton t-shirt available in multiple colors and sizes.',
            'category': categories['Clothing'],
            'buying_price': 8.00,
            'selling_price': 19.99,
            'current_stock': 5,  # Low stock for demonstration
            'reorder_level': 10,
        },
        {
            'item_code': 'BOOK-001',
            'name': 'Python Programming Guide',
            'description': 'Comprehensive guide to Python programming for beginners and intermediate developers.',
            'category': categories['Books'],
            'buying_price': 22.00,
            'selling_price': 39.99,
            'current_stock': 30,
            'reorder_level': 5,
        },
        {
            'item_code': 'HOME-001',
            'name': 'LED Desk Lamp',
            'description': 'Modern LED desk lamp with adjustable brightness and USB charging port.',
            'category': categories['Home & Garden'],
            'buying_price': 28.00,
            'selling_price': 54.99,
            'current_stock': 15,
            'reorder_level': 8,
        },
        {
            'item_code': 'ELEC-003',
            'name': 'Wireless Mouse',
            'description': 'Ergonomic wireless mouse with precision tracking and long battery life.',
            'category': categories['Electronics'],
            'buying_price': 15.00,
            'selling_price': 29.99,
            'current_stock': 40,
            'reorder_level': 12,
        }
    ]
    
    created_count = 0
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            item_code=product_data['item_code'],
            defaults={
                **product_data,
                'status': 'active',
                'created_by': admin_user
            }
        )
        if created:
            created_count += 1
            print(f"✅ Created: {product.item_code} - {product.name}")
        else:
            print(f"📦 Exists: {product.item_code} - {product.name}")
    
    print(f"\n🎉 Sample data creation complete!")
    print(f"📊 Categories: {len(categories_data)}")
    print(f"📦 Products: {len(products_data)} ({created_count} new)")
    print(f"🌐 View at: http://127.0.0.1:9000/products/")

if __name__ == '__main__':
    create_sample_data()
