from django import forms
from .models import Product, Category, Supplier, InventoryTransaction, Purchase, PurchaseItem

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter category description'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check if category name already exists (case-insensitive)
            exists = Category.objects.filter(name__iexact=name)
            if self.instance:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise forms.ValidationError("A category with this name already exists.")
        return name

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'item_code', 'name', 'description', 'category',
            'buying_price', 'selling_price', 'current_stock',
            'reorder_level', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'item_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank for auto-generation'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter product description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'buying_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'current_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_code'].required = False
        self.fields['category'].required = False
        
        # Add required field indicators
        for field in ['name', 'buying_price', 'selling_price', 'current_stock', 'reorder_level']:
            self.fields[field].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        buying_price = cleaned_data.get('buying_price')
        selling_price = cleaned_data.get('selling_price')
        
        if buying_price and selling_price:
            if selling_price < buying_price:
                raise forms.ValidationError(
                    "Selling price cannot be less than buying price."
                )
        
        return cleaned_data

class InventoryTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = [
            'product', 'transaction_type', 'quantity',
            'unit_price', 'reference_number', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_price'].widget.attrs.update({'step': '0.01'})
        
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')
        
        if transaction_type == 'sale' and product and quantity:
            if quantity > product.current_stock:
                raise forms.ValidationError(
                    f"Not enough stock available. Current stock: {product.current_stock}"
                )
        
        return cleaned_data

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter supplier name'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter address'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = False
        self.fields['phone'].required = False
        self.fields['contact_person'].required = False
        self.fields['address'].required = False
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, phone))
            # Check if phone number is valid (at least 10 digits)
            if len(phone) < 10:
                raise forms.ValidationError("Please enter a valid phone number with at least 10 digits.")
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists for another supplier
            if Supplier.objects.filter(email=email).exclude(id=self.instance.id if self.instance else None).exists():
                raise forms.ValidationError("This email is already registered with another supplier.")
        return email

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'purchase_date', 'reference_number', 'status', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={
                'class': 'form-control'
            }),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank for auto-generation'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any additional notes'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reference_number'].required = False
        self.fields['notes'].required = False
        
        # Add required field indicators
        for field in ['supplier', 'purchase_date', 'status']:
            self.fields[field].required = True

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        if quantity is not None and quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        
        if unit_price is not None and unit_price <= 0:
            raise forms.ValidationError("Unit price must be greater than 0.")
        
        return cleaned_data

# Formset for purchase items
PurchaseItemFormSet = forms.inlineformset_factory(
    Purchase, 
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True
)