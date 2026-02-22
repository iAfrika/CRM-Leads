from django import forms
from django.contrib.auth.models import User
from .models import Project, ProjectDocument, ProjectNote, ProjectMilestone, Transaction
from django.utils import timezone
from people.models import Person

class ProjectForm(forms.ModelForm):
    team_members = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'})
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'name', 'code', 'description', 'client', 'start_date', 'end_date',
            'status', 'priority', 'budget', 'manager', 'team_members', 'tags'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={
                'class': 'form-control', 
                'readonly': 'readonly',
                'placeholder': 'Will be auto-generated (e.g., CC-P0001)',
                'style': 'background-color: #f8f9fa; cursor: not-allowed;'
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'client': forms.Select(attrs={'class': 'form-control select2'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control select2'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'data-role': 'tagsinput'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make code field optional and readonly for new projects
        self.fields['code'].required = False
        
        # For existing projects, show the current code
        if self.instance and self.instance.pk:
            self.fields['code'].widget.attrs['readonly'] = 'readonly'
            self.fields['code'].widget.attrs['placeholder'] = self.instance.code
        else:
            # For new projects, show preview of next code
            self.fields['code'].widget.attrs['placeholder'] = self._get_next_code_preview()
    
    def _get_next_code_preview(self):
        """Get a preview of the next project code that will be generated"""
        try:
            last_project = Project.objects.filter(code__startswith='CC-P').order_by('-code').first()
            if last_project:
                # Extract the number from the last code
                last_number = int(last_project.code.split('CC-P')[1])
                next_number = last_number + 1
            else:
                next_number = 1
            return f"CC-P{next_number:04d}"
        except:
            return "CC-P0001"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be earlier than start date.")
        
        # Clear the code field so it doesn't interfere with auto-generation
        # The model's save method will generate it
        if not self.instance.pk:
            cleaned_data['code'] = ''

        return cleaned_data

class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ['title', 'document_type', 'file', 'description', 'version']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProjectNoteForm(forms.ModelForm):
    class Meta:
        model = ProjectNote
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProjectMilestoneForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'})
    )
    
    completed_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
        required=False
    )

    class Meta:
        model = ProjectMilestone
        fields = ['title', 'description', 'due_date', 'completed_date', 'is_completed', 'completion_percentage']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'completion_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_completed = cleaned_data.get('is_completed')
        completion_percentage = cleaned_data.get('completion_percentage')
        completed_date = cleaned_data.get('completed_date')

        if is_completed:
            cleaned_data['completion_percentage'] = 100
            if not completed_date:
                cleaned_data['completed_date'] = timezone.now().date()
        elif not is_completed:
            cleaned_data['completed_date'] = None

        return cleaned_data

class ProjectFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All')] + Project.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All')] + Project.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    client = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Clients",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    manager = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="All Managers",
        widget=forms.Select(attrs={'class': 'form-control select2'})
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search projects...'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from clients.models import Client
        self.fields['client'].queryset = Client.objects.all()

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'description', 'transaction_type', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'placeholder': 'Enter transaction description'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount 