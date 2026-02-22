from django import forms
from django.contrib.auth.models import User
from .models import Lead, LeadActivity, LeadNote, LeadDocument
from people.models import Person
from clients.models import Client


class LeadForm(forms.ModelForm):
    follow_up_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        required=False
    )
    
    website = forms.URLField(required=False)

    class Meta:
        model = Lead
        fields = [
            'title', 'company_name', 'contact_person', 'email', 'phone', 'website',
            'description', 'requirements', 'estimated_value', 'status', 'source',
            'priority', 'follow_up_date', 'assigned_to', 'tags', 'notes_text'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional lead title'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estimated_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'data-role': 'tagsinput'}),
            'notes_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LeadActivityForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        required=False
    )

    class Meta:
        model = LeadActivity
        fields = ['activity_type', 'description', 'due_date']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LeadFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All')] + Lead.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    source = forms.ChoiceField(
        choices=[('', 'All')] + Lead.SOURCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All')] + Lead.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    assigned_to = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        required=False,
        empty_label="All Users",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_range = forms.ChoiceField(
        choices=[
            ('', 'All Time'),
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('quarter', 'This Quarter'),
            ('year', 'This Year'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search leads...'})
    ) 

class LeadNoteForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': 'Enter your note here...',
            'required': 'required'
        }),
        max_length=1000,
        min_length=1,
        error_messages={
            'required': 'Note content cannot be empty.',
            'max_length': 'Note is too long. Maximum 1000 characters allowed.',
            'min_length': 'Note is too short. Minimum 1 character required.'
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = 'Note Content'

    class Meta:
        model = LeadNote
        fields = ['content']

class LeadDocumentForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'required': 'required'
        }),
        error_messages={
            'required': 'Please upload a document.',
            'invalid_extension': 'File type not supported.'
        }
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Optional description for the document...'
        }),
        required=False,
        max_length=500,
        error_messages={
            'max_length': 'Description is too long. Maximum 500 characters allowed.'
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].label = 'Document File'
        self.fields['description'].label = 'Description (Optional)'

    class Meta:
        model = LeadDocument
        fields = ['file', 'description']
        
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        # Validate file size (max 10MB)
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError("File size must be under 10MB.")
        
        return file