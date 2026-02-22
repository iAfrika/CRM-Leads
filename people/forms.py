from django import forms
from .models import Person, Role, ContactHistory

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email', 'phone', 
                  'telegram_username', 'address', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_telegram_username(self):
        telegram_username = self.cleaned_data.get('telegram_username')
        if telegram_username:
            # Check if this telegram username already exists (exclude current instance if updating)
            if self.instance.pk:
                exists = Person.objects.filter(telegram_username=telegram_username).exclude(pk=self.instance.pk).exists()
            else:
                exists = Person.objects.filter(telegram_username=telegram_username).exists()
                
            if exists:
                raise forms.ValidationError("This Telegram username is already in use.")
        return telegram_username
    
class RoleAssignmentForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['role']
        widgets = {
            'role': forms.CheckboxSelectMultiple(),
        }

class ContactForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True
    )
    
    class Meta:
        model = ContactHistory
        fields = ['contact_type', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }