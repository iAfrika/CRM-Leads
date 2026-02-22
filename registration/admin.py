from django.contrib import admin
from .models import (PaymentMethod, SubscriptionPlan, Company, Subscription, 
                    PaymentTransaction, CompanyUser, CompanyBankAccount, AppModule, CompanyApp)  

# Register your models here.

class CompanyBankAccountInline(admin.TabularInline):
    model = CompanyBankAccount
    extra = 0
    fields = ('bank_name', 'account_name', 'account_number', 'account_type', 'swift_code', 'is_primary', 'is_active')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_monthly', 'price_annually', 'is_active')
    list_editable = ('price_monthly', 'price_annually', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'created_at')
    search_fields = ('name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CompanyBankAccountInline]

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'plan')
    search_fields = ('company__name', 'plan__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_name', 'account_number', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('account_name', 'account_number')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('company', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'payment_date')
    search_fields = ('company__name', 'transaction_reference')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'company')
    search_fields = ('user__username', 'user__email', 'company__name')
    list_editable = ('role', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['user', 'company', 'invited_by']

@admin.register(CompanyBankAccount)
class CompanyBankAccountAdmin(admin.ModelAdmin):
    list_display = ('company', 'bank_name', 'account_name', 'account_number', 'account_type', 'is_primary', 'is_active')
    list_filter = ('account_type', 'is_primary', 'is_active', 'bank_name')
    search_fields = ('company__name', 'bank_name', 'account_name', 'account_number')
    list_editable = ('is_primary', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['company']


@admin.register(AppModule)
class AppModuleAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'order', 'is_active', 'requires_subscription')
    list_editable = ('order', 'is_active', 'requires_subscription')
    list_filter = ('is_active', 'requires_subscription')
    search_fields = ('name', 'display_name', 'description')
    ordering = ('order', 'display_name')


class CompanyAppInline(admin.TabularInline):
    model = CompanyApp
    extra = 0
    fields = ('app_module', 'is_enabled', 'enabled_at', 'enabled_by')
    readonly_fields = ('enabled_at',)
    autocomplete_fields = ['app_module', 'enabled_by']


@admin.register(CompanyApp)
class CompanyAppAdmin(admin.ModelAdmin):
    list_display = ('company', 'app_module', 'is_enabled', 'enabled_at', 'enabled_by')
    list_filter = ('is_enabled', 'app_module', 'enabled_at')
    search_fields = ('company__name', 'app_module__name', 'app_module__display_name')
    list_editable = ('is_enabled',)
    readonly_fields = ('enabled_at',)
    autocomplete_fields = ['company', 'app_module', 'enabled_by']
    date_hierarchy = 'enabled_at'
