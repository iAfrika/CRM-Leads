from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'total_amount', 'payment_status', 'sale_date']
    list_filter = ['payment_status', 'payment_method', 'sale_date']
    search_fields = ['client__name', 'description']
    date_hierarchy = 'sale_date'
    inlines = [SaleItemInline]

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'description', 'quantity', 'unit_price', 'discount', 'get_total']
    list_filter = ['sale__sale_date']
    search_fields = ['description', 'sale__client__name']

