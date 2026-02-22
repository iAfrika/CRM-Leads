from django import forms
from django.contrib.auth.models import User
from .models import Account, Transaction
from project_management.models import Project
from registration.models import CompanyBankAccount


class AccountCreationForm(forms.ModelForm):
    """Form for selecting company bank account and associating with project"""
    
    company_bank_account = forms.ModelChoiceField(
        queryset=CompanyBankAccount.objects.none(),
        required=True,
        empty_label="-- Select a Company Bank Account --",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'company_bank_account',
            'style': 'width: 100%; max-width: 100%;'
        }),
        help_text="Select a bank account from your company's registered accounts."
    )
    
    def label_from_instance(self, obj):
        """Custom label for bank account dropdown"""
        return f"{obj.bank_name} - Acc: {obj.account_number}"
    
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        empty_label="-- Select a Project (Optional) --",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'project'
        }),
        help_text="Optionally associate this account with a project for tracking."
    )
    
    account_type = forms.ChoiceField(
        choices=Account.ACCOUNT_TYPES,
        initial='COMPANY',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'account_type'
        }),
        help_text="Choose the type of account."
    )

    class Meta:
        model = Account
        fields = ['company_bank_account', 'account_type', 'project']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Populate company bank accounts if company is provided
        if self.company:
            self.fields['company_bank_account'].queryset = CompanyBankAccount.objects.filter(
                company=self.company,
                is_active=True
            ).order_by('-is_primary', 'bank_name')
            # Set custom label method
            self.fields['company_bank_account'].label_from_instance = lambda obj: f"{obj.bank_name} - {obj.account_number}"
        
        # Update the project queryset to show active projects only
        self.fields['project'].queryset = Project.objects.all().order_by('name')
        
    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')
        project = cleaned_data.get('project')
        
        # If account type is PROJECT, project selection is required
        if account_type == 'PROJECT' and not project:
            raise forms.ValidationError("You must select a project for a Project Account.")
            
        # If account type is COMPANY, project should not be selected
        if account_type == 'COMPANY' and project:
            cleaned_data['project'] = None  # Clear the project for company accounts
            
        return cleaned_data
        
    def save(self, commit=True):
        account = super().save(commit=False)
        
        if self.user:
            account.owner_id = self.user.id
        
        # Get the selected company bank account
        company_bank_account = self.cleaned_data.get('company_bank_account')
        if company_bank_account:
            account.company_bank_account_id = company_bank_account.id
            # Use the company bank account number
            account.account_number = company_bank_account.account_number
        
        # Set company account flag
        if account.account_type == 'COMPANY':
            account.is_main_company_account = True
            
        if commit:
            account.save()
        return account


class DepositForm(forms.Form):
    """Form for depositing funds into an account"""
    
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount to deposit',
            'step': '0.01'
        }),
        help_text="Enter the amount you want to deposit."
    )
    
    description = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Description (optional)'
        }),
        help_text="Optional description for this deposit."
    )


class WithdrawForm(forms.Form):
    """Form for withdrawing funds from an account"""
    
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount to withdraw',
            'step': '0.01'
        }),
        help_text="Enter the amount you want to withdraw."
    )
    
    description = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Description (optional)'
        }),
        help_text="Optional description for this withdrawal."
    )


class TransferForm(forms.Form):
    """Form for transferring funds between accounts"""
    
    destination_account = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter destination account number'
        }),
        help_text="Enter the account number to transfer to."
    )
    
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount to transfer',
            'step': '0.01'
        }),
        help_text="Enter the amount you want to transfer."
    )
    
    description = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Description (optional)'
        }),
        help_text="Optional description for this transfer."
    )
