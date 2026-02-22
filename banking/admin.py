from django.contrib import admin
from .models import Account, Transaction, Debt, Tax

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'account_type', 'owner_id', 'balance', 'is_active', 'created_at')
    list_filter = ('account_type', 'is_active')
    search_fields = ('account_number',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'account', 'transaction_type', 'amount', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('account__account_number', 'description')
    readonly_fields = ('transaction_id', 'timestamp')

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('debt_type', 'account', 'principal_amount', 'remaining_amount', 'interest_rate', 'is_active')
    list_filter = ('debt_type', 'is_active')
    search_fields = ('account__account_number',)

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'account', 'amount', 'date_applied')
    list_filter = ('tax_type', 'date_applied')
    search_fields = ('account__account_number', 'description')
