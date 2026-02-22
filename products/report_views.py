from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Value, Case, When, IntegerField
from decimal import Decimal
from .models import Product, Category
from purchases.models import Purchase

@login_required
def inventory_report(request):
    # Get all active products
    products = Product.objects.filter(is_active=True).select_related('category')
    
    # Get all categories for the filter dropdown
    categories = Category.objects.filter(is_active=True)
    
    # Calculate inventory statistics
    total_products = products.count()
    products_in_stock = products.filter(stock_quantity__gt=0).count()
    
    # Calculate low stock and out of stock products
    # Assuming products with stock below or equal to reorder level are considered low stock
    low_stock_products = products.filter(stock_quantity__gt=0).filter(stock_quantity__lte=10).count()
    out_of_stock_products = products.filter(stock_quantity=0).count()
    
    # Calculate total inventory value
    total_inventory_value = sum(product.price * product.stock_quantity for product in products)
    
    # Add computed values to products
    for product in products:
        product.current_stock = product.stock_quantity
        product.reorder_level = 10  # This could be made configurable per product
        product.unit_price = product.price
        product.inventory_value = product.price * product.stock_quantity
    
    context = {
        'products': products,
        'categories': categories,
        'total_products': total_products,
        'products_in_stock': products_in_stock,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_inventory_value': total_inventory_value,
        'app_name': 'products'
    }
    
    return render(request, 'products/reports/inventory_report.html', context)

@login_required
def purchases_report(request):
    # Get all purchases
    purchases = Purchase.objects.all()
    
    # Calculate purchase statistics
    total_purchases = purchases.count()
    total_spent = purchases.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get purchase history grouped by product
    product_purchases = purchases.values('title').annotate(
        total_quantity=Sum('quantity'),
        total_cost=Sum('amount')
    ).order_by('-total_cost')
    
    context = {
        'purchase_items': purchases,
        'total_purchases': total_purchases,
        'total_spent': total_spent,
        'product_purchases': product_purchases,
        'app_name': 'products'
    }
    
    return render(request, 'products/reports/purchases_report.html', context)