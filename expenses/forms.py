from django import forms
from .models import Expense, ExpenseCategory, RecurringExpense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'title',
            'amount',
            'category',
            'date',
            'payment_method',
            'description',
            'receipt'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class RecurringExpenseForm(forms.ModelForm):
    class Meta:
        model = RecurringExpense
        fields = ['title', 'amount', 'category', 'frequency', 'next_date', 'is_active']
        widgets = {
            'next_date': forms.DateInput(attrs={'type': 'date'}),
        } 