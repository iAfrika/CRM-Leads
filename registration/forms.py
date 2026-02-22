from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CompanyUser, Company, CompanyBankAccount

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            
        # Add placeholders
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter your first name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter your last name'})
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email address'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CompanyUserAssignmentForm(forms.ModelForm):
    class Meta:
        model = CompanyUser
        fields = ('user', 'role', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, company=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        
        # Display user with their full name and email
        self.fields['user'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.email})"
        
        # Filter out users already assigned to this company
        if company:
            existing_users = CompanyUser.objects.filter(company=company).values_list('user_id', flat=True)
            self.fields['user'].queryset = User.objects.exclude(id__in=existing_users)

class ExistingUserAssignmentForm(forms.Form):
    email = forms.EmailField(
        label="User Email", 
        help_text="Enter the email of an existing user to assign to this company."
    )
    role = forms.ChoiceField(
        choices=CompanyUser.ROLE_CHOICES,
        initial='staff',
        help_text="Select the role for this user in the company."
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Optional notes about this user's role or responsibilities."
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
            self.user = user
        except User.DoesNotExist:
            raise ValidationError("No user found with this email address. Please register them first.")
        return email

class UserInvitationForm(forms.Form):
    email = forms.EmailField(
        label="Email Address", 
        help_text="Enter the email address to send an invitation to."
    )
    role = forms.ChoiceField(
        choices=CompanyUser.ROLE_CHOICES,
        initial='staff',
        help_text="Select the role for this user in the company."
    )
    first_name = forms.CharField(
        required=False,
        help_text="Optional: Provide the first name of the person you're inviting."
    )
    last_name = forms.CharField(
        required=False,
        help_text="Optional: Provide the last name of the person you're inviting."
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Optional message to include in the invitation email."
    )

class CompanyEditForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name', 'initials', 'phone_number', 'email', 'logo', 'tax_pin', 'physical_address', 'postal_address', 'currency', 'timezone')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'initials': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10', 'style': 'text-transform: uppercase;', 'placeholder': 'e.g., CC, ABC'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tax_pin': forms.TextInput(attrs={'class': 'form-control'}),
            'physical_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'postal_address': forms.TextInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Common currency choices
        self.fields['currency'].widget = forms.Select(
            choices=[
                ('KES', 'Kenyan Shilling (KES)'),
                ('USD', 'US Dollar (USD)'),
                ('EUR', 'Euro (EUR)'),
                ('GBP', 'British Pound (GBP)'),
                ('TZS', 'Tanzanian Shilling (TZS)'),
                ('UGX', 'Ugandan Shilling (UGX)'),
            ],
            attrs={'class': 'form-control'}
        )
        
        # Common timezone choices for East Africa
        self.fields['timezone'].widget = forms.Select(
            choices=[
                ('Africa/Nairobi', 'Nairobi (UTC+3)'),
                ('Africa/Kampala', 'Kampala (UTC+3)'),
                ('Africa/Dar_es_Salaam', 'Dar es Salaam (UTC+3)'),
                ('UTC', 'UTC'),
            ],
            attrs={'class': 'form-control'}
        )

class CompanyBankAccountForm(forms.ModelForm):
    class Meta:
        model = CompanyBankAccount
        fields = ('bank_name', 'account_name', 'account_number', 'account_type', 
                 'swift_code', 'iban', 'branch_name', 'branch_code', 'routing_number', 
                 'is_primary', 'is_active', 'notes')
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Kenya Commercial Bank'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account holder name as per bank records'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1234567890'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'swift_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., KCBLKENX'}),
            'iban': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'International Bank Account Number'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Nairobi Main Branch'}),
            'branch_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 001'}),
            'routing_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'For US banks'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes about this account'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set is_active to True by default for new accounts
        if not self.instance.pk:
            self.fields['is_active'].initial = True

# Django Formset for managing multiple bank accounts
CompanyBankAccountFormSet = forms.inlineformset_factory(
    Company, 
    CompanyBankAccount,
    form=CompanyBankAccountForm,
    extra=1,  # Show one empty form by default
    can_delete=True,
    min_num=0,
    validate_min=False
)
