from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'item_code', 'buying_price', 'current_stock', 'category', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'description', 'sku', 'category']
        }),
        ('Pricing and Stock', {
            'fields': ['price', 'stock_quantity']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]