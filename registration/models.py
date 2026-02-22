from django.db import models
from django.conf import settings
from django.utils import timezone

def company_logo_path(instance, filename):
    """
    Generate a unique path for company logos.
    Format: company_logos/company_id/filename
    """
    return f'company_logos/{instance.id}/{filename}'

class PaymentMethod(models.Model):
    PAYMENT_CHOICES = [
        ('card', 'Debit/Credit Card'),
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
    ]
    
    name = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    account_number = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_name_display()} - {self.account_name}"

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_annually = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name='Company Name')
    initials = models.CharField(max_length=10, verbose_name='Company Initials', help_text='2-5 characters (e.g., CC, ABC)', blank=True)
    phone_number = models.CharField(max_length=20, verbose_name='Phone Number')
    email = models.EmailField(verbose_name='Email Address')
    logo = models.ImageField(upload_to=company_logo_path, null=True, blank=True, verbose_name='Company Logo')
    tax_pin = models.CharField(max_length=50, verbose_name='Tax PIN')
    physical_address = models.TextField(verbose_name='Physical Address')
    postal_address = models.CharField(max_length=100, null=True, blank=True, verbose_name='Postal Address')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    database_name = models.CharField(max_length=100, unique=True)
    currency = models.CharField(max_length=3, default='KES')
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_companies'
    )

    def __str__(self):
        return self.name

class Subscription(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.plan.name}"

class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100, unique=True)
    external_reference = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.company.name} - {self.amount} - {self.status}"
        
class CompanyUser(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
        ('manager', 'Manager'),
        ('viewer', 'Viewer'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_users')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='sent_invitations'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('company', 'user')
        verbose_name = 'Company User'
        verbose_name_plural = 'Company Users'
        
    def __str__(self):
        return f"{self.user.username} - {self.company.name} - {self.get_role_display()}"

class CompanyBankAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('business', 'Business Account'),
        ('current', 'Current Account'),
        ('fixed_deposit', 'Fixed Deposit'),
        ('other', 'Other'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_name = models.CharField(max_length=100, verbose_name='Bank Name')
    account_name = models.CharField(max_length=100, verbose_name='Account Holder Name')
    account_number = models.CharField(max_length=50, verbose_name='Account Number')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='business', verbose_name='Account Type')
    swift_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='SWIFT/BIC Code')
    iban = models.CharField(max_length=50, blank=True, null=True, verbose_name='IBAN')
    branch_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Branch Name')
    branch_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Branch Code')
    routing_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Routing Number')
    is_primary = models.BooleanField(default=False, verbose_name='Primary Account')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    notes = models.TextField(blank=True, null=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company Bank Account'
        verbose_name_plural = 'Company Bank Accounts'
        unique_together = ('company', 'account_number', 'bank_name')
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary account per company
        if self.is_primary:
            CompanyBankAccount.objects.filter(company=self.company, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class AppModule(models.Model):
    """
    Represents an available application module in the system
    """
    APP_CHOICES = [
        ('clients', 'Clients Management'),
        ('leads', 'Leads Management'),
        ('sales', 'Sales Management'),
        ('projects', 'Project Management'),
        ('documents', 'Document Management'),
        ('expenses', 'Expense Tracking'),
        ('purchases', 'Purchase Management'),
        ('banking', 'Banking & Finance'),
        ('reports', 'Reports & Analytics'),
        ('people', 'People Management'),
        ('communication', 'Communication'),
        ('dashboard', 'Dashboard'),
    ]
    
    name = models.CharField(max_length=50, unique=True, choices=APP_CHOICES)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-puzzle-piece')
    is_active = models.BooleanField(default=True)
    requires_subscription = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'display_name']
        verbose_name = 'App Module'
        verbose_name_plural = 'App Modules'
    
    def __str__(self):
        return self.display_name


class CompanyApp(models.Model):
    """
    Many-to-many relationship between companies and app modules
    Tracks which apps are enabled for each company
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='enabled_apps')
    app_module = models.ForeignKey(AppModule, on_delete=models.CASCADE, related_name='companies')
    is_enabled = models.BooleanField(default=True)
    enabled_at = models.DateTimeField(auto_now_add=True)
    enabled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='enabled_company_apps'
    )
    settings = models.JSONField(default=dict, blank=True)  # For app-specific settings
    
    class Meta:
        unique_together = ('company', 'app_module')
        verbose_name = 'Company App'
        verbose_name_plural = 'Company Apps'
        ordering = ['app_module__order', 'app_module__display_name']
    
    def __str__(self):
        return f"{self.company.name} - {self.app_module.display_name}"
