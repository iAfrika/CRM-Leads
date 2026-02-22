from django.db import models
from django.utils import timezone
from django.db.models import Sum
import uuid

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('COMPANY', 'Company Main Account'),
        ('PROJECT', 'Project Account'),
    #     ('SAVINGS', 'Savings Account'),
    #     ('CHECKING', 'Checking Account'),
    #     ('CREDIT', 'Credit Account'),
    #     ('LOAN', 'Loan Account'),
    )
    
    # Link to the actual company bank account from company details
    company_bank_account_id = models.IntegerField(null=True, blank=True, help_text="Reference to CompanyBankAccount")
    
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    owner_id = models.IntegerField(default=1)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey('project_management.Project', on_delete=models.CASCADE, related_name='banking_accounts', null=True, blank=True)
    is_main_company_account = models.BooleanField(default=False, help_text="Is this the main company account that tracks all finances?")
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['is_main_company_account'], condition=models.Q(is_main_company_account=True), name='unique_main_company_account')
        ]
    
    def __str__(self):
        if self.is_main_company_account:
            return f"Main Company Account - {self.account_number}"
        elif self.project:
            return f"Project Account ({self.project.name}) - {self.account_number}"
        else:
            return f"{self.account_type} - {self.account_number}"
    
    def get_company_bank_account(self):
        """Get the linked CompanyBankAccount object"""
        if self.company_bank_account_id:
            from registration.models import CompanyBankAccount
            try:
                return CompanyBankAccount.objects.get(id=self.company_bank_account_id)
            except CompanyBankAccount.DoesNotExist:
                return None
        return None
    
    def deposit(self, amount, description=None):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.save()
        
        # Create transaction record
        transaction = Transaction.objects.create(
            account=self,
            transaction_type='DEPOSIT',
            amount=amount,
            description=description or f"Deposit to {self.account_number}"
        )
        
        # If this is a project account, also update the main company account
        if self.project and not self.is_main_company_account:
            main_account = Account.objects.filter(is_main_company_account=True).first()
            if main_account:
                main_account.deposit(amount, f"Project Income: {self.project.name} - {description or 'Deposit'}")
        
        return transaction
    
    def withdraw(self, amount, description=None):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.save()
        
        # Create transaction record
        transaction = Transaction.objects.create(
            account=self,
            transaction_type='WITHDRAWAL',
            amount=amount,
            description=description or f"Withdrawal from {self.account_number}"
        )
        
        # If this is a project account, also update the main company account
        if self.project and not self.is_main_company_account:
            main_account = Account.objects.filter(is_main_company_account=True).first()
            if main_account:
                main_account.withdraw(amount, f"Project Expense: {self.project.name} - {description or 'Withdrawal'}")
        
        return transaction
    
    def transfer(self, destination_account, amount, description=None):
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        
        self.balance -= amount
        destination_account.balance += amount
        self.save()
        destination_account.save()
        
        # Create transaction records for both accounts
        transaction_out = Transaction.objects.create(
            account=self,
            transaction_type='TRANSFER_OUT',
            amount=amount,
            description=description or f"Transfer to {destination_account.account_number}",
            related_account=destination_account
        )
        
        Transaction.objects.create(
            account=destination_account,
            transaction_type='TRANSFER_IN',
            amount=amount,
            description=description or f"Transfer from {self.account_number}",
            related_account=self
        )
        
        return transaction_out
    
    def get_revenue(self):
        """Get the total revenue (income) for this account"""
        revenue_transactions = self.transactions.filter(
            transaction_type__in=['DEPOSIT', 'TRANSFER_IN', 'PAYMENT_RECEIVED']
        )
        return revenue_transactions.aggregate(total=Sum('amount'))['total'] or 0
    
    def get_expenditure(self):
        """Get the total expenditure (outgoing money) for this account"""
        expenditure_transactions = self.transactions.filter(
            transaction_type__in=['WITHDRAWAL', 'TRANSFER_OUT', 'PAYMENT_SENT']
        )
        return expenditure_transactions.aggregate(total=Sum('amount'))['total'] or 0
    
    def get_profit_loss(self):
        """Calculate profit/loss (revenue - expenditure)"""
        revenue = self.get_revenue()
        expenditure = self.get_expenditure()
        return revenue - expenditure

class ProjectFinancialSummary(models.Model):
    """Model to store pre-calculated financial summaries for projects"""
    project = models.OneToOneField('project_management.Project', on_delete=models.CASCADE, related_name='financial_summary')
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Financial Summary - {self.project.name}"
    
    def update_summary(self):
        """Update the financial summary based on the project's account transactions"""
        account = self.project.banking_accounts.first()
        if account:
            self.total_revenue = account.get_revenue()
            self.total_expenses = account.get_expenditure()
            self.total_profit = account.get_profit_loss()
            self.save()
        return self

class Debt(models.Model):
    DEBT_TYPES = (
        ('LOAN', 'Loan'),
        ('CREDIT', 'Credit Card'),
        ('MORTGAGE', 'Mortgage'),
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='debts')
    debt_type = models.CharField(max_length=20, choices=DEBT_TYPES)
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual interest rate
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    project = models.ForeignKey('project_management.Project', on_delete=models.SET_NULL, related_name='banking_debts', null=True, blank=True)
    
    def __str__(self):
        if self.project:
            return f"{self.debt_type} - {self.project.name}"
        return f"{self.debt_type} - {self.account.account_number}"
    
    def calculate_interest(self):
        # Calculate monthly interest
        monthly_rate = self.interest_rate / 12 / 100
        return self.remaining_amount * monthly_rate

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER_IN', 'Transfer In'),
        ('TRANSFER_OUT', 'Transfer Out'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('PAYMENT_SENT', 'Payment Sent'),
        ('FEE', 'Fee'),
        ('INTEREST', 'Interest'),
        ('TAX', 'Tax'),
        ('INVOICE', 'Invoice'),
        ('EXPENSE', 'Expense'),
        ('PURCHASE', 'Purchase'),
    )
    
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    related_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_transactions')
    project = models.ForeignKey('project_management.Project', on_delete=models.SET_NULL, related_name='banking_transactions', null=True, blank=True)
    # Using string references to prevent app dependency issues
    invoice = models.ForeignKey('sales.Invoice', on_delete=models.SET_NULL, related_name='transactions', null=True, blank=True)
    expense = models.ForeignKey('expenses.Expense', on_delete=models.SET_NULL, related_name='transactions', null=True, blank=True)
    purchase = models.ForeignKey('purchases.Purchase', on_delete=models.SET_NULL, related_name='transactions', null=True, blank=True)
    
    def __str__(self):
        if self.project:
            return f"{self.transaction_type} - {self.amount} - {self.project.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
        return f"{self.transaction_type} - {self.amount} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # If transaction is linked to a project but not to a project account, link it to the project account
        if self.project and not self.account.project:
            project_account = Account.objects.filter(project=self.project).first()
            if project_account:
                self.account = project_account
        
        super().save(*args, **kwargs)
        
        # Update project financial summary if this transaction is project-related
        if self.project:
            summary, created = ProjectFinancialSummary.objects.get_or_create(project=self.project)
            summary.update_summary()

class Tax(models.Model):
    TAX_TYPES = (
        ('INCOME', 'Income Tax'),
        ('TRANSACTION', 'Transaction Tax'),
        ('INTEREST', 'Interest Tax'),
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='taxes')
    tax_type = models.CharField(max_length=20, choices=TAX_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    date_applied = models.DateField()
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='taxes', null=True, blank=True)
    project = models.ForeignKey('project_management.Project', on_delete=models.SET_NULL, related_name='banking_taxes', null=True, blank=True)
    
    def __str__(self):
        if self.project:
            return f"{self.tax_type} - {self.amount} - {self.project.name} - {self.date_applied}"
        return f"{self.tax_type} - {self.amount} - {self.date_applied}"
