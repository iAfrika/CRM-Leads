from django import forms
from .models import Purchase, PurchaseCategory

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = [
            'title',
            'unit_price',
            'quantity',
            'category',
            'vendor',
            'date',
            'due_date',
            'status',
            'payment_method',
            'description',
            'invoice'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the amount field read-only since it's calculated
        if 'amount' in self.fields:
            self.fields['amount'].widget.attrs['readonly'] = True

class PurchaseCategoryForm(forms.ModelForm):
    class Meta:
        model = PurchaseCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        } 