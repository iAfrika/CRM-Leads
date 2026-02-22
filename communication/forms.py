from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import (
    Contact, 
    Email, 
    EmailAttachment, 
    Event, 
    WhatsAppMessage, 
    TelegramMessage,
    Notification,
    TelegramContact,
    TelegramChat,
    TelegramSession,
    TelegramBot
)

User = get_user_model()

class MultipleFileInput(forms.ClearableFileInput):
    """
    Custom file input to support multiple file uploads.
    """
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    """
    Custom file field to support multiple file uploads.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """
        Validate multiple file uploads.
        """
        if not data and initial:
            return initial

        if not data:
            return None

        files = data if isinstance(data, list) else [data]
        
        # Validate each file
        for file in files:
            super().clean(file)
        
        return files

class ContactForm(forms.ModelForm):
    """
    Form for creating and updating contacts
    """
    class Meta:
        model = Contact
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'messenger_type', 
            'messenger_id', 
            'company', 
            'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'messenger_type': forms.Select(attrs={'class': 'form-select'}),
            'messenger_id': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """
        Set the user for the contact.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Associate the contact with the current user.
        """
        contact = super().save(commit=False)
        if self.user:
            contact.user = self.user
        
        if commit:
            contact.save()
        return contact

class EmailComposeForm(forms.ModelForm):
    """
    Form for composing and sending emails with multiple attachments.
    """
    # Define recipients and cc as separate fields since they're ManyToMany
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=True,
        help_text='Select one or more recipients'
    )
    
    cc = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        help_text='Select users to CC (optional)'
    )
    
    attachments = MultipleFileField(
        required=False,
        help_text='Select multiple files to attach (PDF, DOC, DOCX, JPG, PNG, TXT, XLSX)',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'png', 'txt', 'xlsx'])]
    )

    class Meta:
        model = Email
        fields = ['recipients', 'cc', 'subject', 'body', 'attachments']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Compose your message here...'})
        }
    
    def __init__(self, *args, **kwargs):
        """
        Set up user-specific recipient lists
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Get all users for the same company as the current user
            # This assumes there's a Profile model with a company field
            self.fields['recipients'].queryset = User.objects.exclude(id=user.id)
            self.fields['cc'].queryset = User.objects.exclude(id=user.id)
            
            # If we're editing an existing email
            if self.instance and self.instance.pk:
                # Pre-select recipients and cc
                if hasattr(self.instance, 'recipients'):
                    self.initial['recipients'] = self.instance.recipients.all()
                if hasattr(self.instance, 'cc'):
                    self.initial['cc'] = self.instance.cc.all()

    def clean(self):
        """
        Validate the form data
        """
        cleaned_data = super().clean()
        
        # Ensure at least one recipient is selected
        if not cleaned_data.get('recipients'):
            self.add_error('recipients', 'You must specify at least one recipient')
            
        # Ensure subject is not empty
        if not cleaned_data.get('subject'):
            self.add_error('subject', 'Subject cannot be empty')
            
        return cleaned_data

    def save(self, commit=True):
        """
        Save email and handle multiple attachments.
        """
        email = super().save(commit=False)
        
        if commit:
            email.save()

        # Handle attachments
        if self.cleaned_data.get('attachments'):
            for uploaded_file in self.cleaned_data['attachments']:
                attachment = EmailAttachment.objects.create(file=uploaded_file)
                email.attachments.add(attachment)

        return email

class EventForm(forms.ModelForm):
    """
    Form for creating and editing calendar events with comprehensive functionality.
    """
    # Additional fields for enhanced event creation
    attendee_emails = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter email addresses separated by comma'}),
        help_text='Add additional attendees by email'
    )
    
    # Recurrence fields
    is_recurring = forms.BooleanField(
        required=False, 
        label='Make this a recurring event',
        help_text='Check if this event repeats periodically'
    )
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_time', 'end_time', 
            'location', 'category', 'privacy', 'color',
            'recurrence_type', 'recurrence_interval', 'recurrence_end_date',
            'send_email_reminder', 'send_sms_reminder', 'send_whatsapp_reminder',
            'video_conference_link', 'external_link'
        ]
        
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'color': forms.TextInput(attrs={'type': 'color'}),
            'recurrence_end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        """
        Validate form data with comprehensive checks.
        """
        cleaned_data = super().clean()
        
        # Validate time range
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("End time must be after start time.")
        
        # Validate recurring event details
        is_recurring = cleaned_data.get('is_recurring')
        recurrence_type = cleaned_data.get('recurrence_type')
        recurrence_interval = cleaned_data.get('recurrence_interval')
        
        if is_recurring:
            if recurrence_type == 'none':
                raise forms.ValidationError("Please select a recurrence type for recurring events.")
            
            if recurrence_interval < 1:
                raise forms.ValidationError("Recurrence interval must be at least 1.")
        
        # Process attendee emails
        attendee_emails = cleaned_data.get('attendee_emails', '').strip()
        if attendee_emails:
            email_list = [email.strip() for email in attendee_emails.split(',')]
            # Validate email format and find corresponding contacts
            valid_contacts = []
            for email in email_list:
                try:
                    contact = Contact.objects.get(email__iexact=email)
                    valid_contacts.append(contact)
                except Contact.DoesNotExist:
                    raise forms.ValidationError(f"No contact found with email: {email}")
            
            cleaned_data['attendees'] = valid_contacts
        
        return cleaned_data
    
    def save(self, user, commit=True):
        """
        Custom save method to associate the event with the current user.
        """
        event = super().save(commit=False)
        event.user = user
        
        if commit:
            event.save()
            
            # Handle many-to-many relationships after saving
            if 'attendees' in self.cleaned_data:
                event.attendees.set(self.cleaned_data['attendees'])
        
        return event

class WhatsAppMessageForm(forms.ModelForm):
    """
    Form for creating WhatsApp messages
    """
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Recipient Contact'
    )
    message_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': 'Type your WhatsApp message...'
        }),
        label='Message',
        max_length=1000
    )
    media_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label='Optional Media File'
    )

    class Meta:
        model = WhatsAppMessage
        fields = ['contact', 'message_text', 'media_file']

    def __init__(self, *args, **kwargs):
        """
        Limit contact queryset to user's contacts
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['contact'].queryset = Contact.objects.filter(user=user)

    def clean_message_text(self):
        """
        Validate message body
        """
        message_text = self.cleaned_data['message_text']
        if len(message_text.strip()) == 0:
            raise forms.ValidationError('Message cannot be empty.')
        return message_text

class TelegramMessageForm(forms.ModelForm):
    """
    Enhanced form for creating Telegram messages
    """
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Recipient Contact',
        required=False
    )
    
    telegram_contact = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        label='Telegram Contact',
        required=False
    )
    
    message_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control telegram-message-input', 
            'rows': 4, 
            'placeholder': 'Type your message...',
            'data-emoji': 'true'
        }),
        label='Message',
        max_length=4096,  # Telegram's message limit
        required=False
    )
    
    media_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx,.txt'
        }),
        label='Media File (Photo, Video, Audio, Document)',
        validators=[FileExtensionValidator([
            'jpg', 'jpeg', 'png', 'gif', 'webp',  # Images
            'mp4', 'avi', 'mov', 'webm',          # Videos
            'mp3', 'ogg', 'wav', 'flac',          # Audio
            'pdf', 'doc', 'docx', 'txt', 'zip'    # Documents
        ])]
    )
    
    media_caption = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional caption for media...'
        }),
        label='Media Caption',
        max_length=1024,
        required=False
    )
    
    reply_to_message_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    schedule_send = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        label='Schedule Send (Optional)',
        required=False
    )

    class Meta:
        model = TelegramMessage
        fields = [
            'contact', 'telegram_contact', 'message_text', 'media_file', 
            'media_caption', 'reply_to_message_id', 'schedule_send'
        ]

    def __init__(self, *args, **kwargs):
        """
        Limit querysets to user's contacts
        """
        user = kwargs.pop('user', None)
        chat = kwargs.pop('chat', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Regular CRM contacts
            self.fields['contact'].queryset = Contact.objects.filter(
                user=user,
                messenger_type='telegram'
            )
            
            # Telegram-specific contacts
            from .models import TelegramContact
            self.fields['telegram_contact'].queryset = TelegramContact.objects.filter(
                user=user
            )
        
        # If editing an existing message or replying
        if chat:
            self.fields['contact'].initial = chat.contact
            if hasattr(chat, 'telegram_contact'):
                self.fields['telegram_contact'].initial = chat.contact

    def clean(self):
        """
        Validate form data
        """
        cleaned_data = super().clean()
        message_text = cleaned_data.get('message_text', '').strip()
        media_file = cleaned_data.get('media_file')
        
        # Must have either text or media
        if not message_text and not media_file:
            raise forms.ValidationError('You must provide either a message or media file.')
        
        # Validate message length
        if message_text and len(message_text) > 4096:
            raise forms.ValidationError('Message is too long. Telegram messages are limited to 4096 characters.')
        
        # Validate media caption
        media_caption = cleaned_data.get('media_caption', '')
        if media_caption and len(media_caption) > 1024:
            raise forms.ValidationError('Media caption is too long. Captions are limited to 1024 characters.')
        
        return cleaned_data

class TelegramContactForm(forms.ModelForm):
    """
    Form for managing Telegram contacts
    """
    
    class Meta:
        model = TelegramContact
        fields = [
            'first_name', 'last_name', 'username', 'phone_number',
            'bio', 'is_verified', 'is_premium', 'is_bot'
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Without @ symbol'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_premium': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_bot': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_username(self):
        """Validate username format"""
        username = self.cleaned_data.get('username', '').strip()
        if username:
            # Remove @ if present
            username = username.lstrip('@')
            # Validate format
            if not username.replace('_', '').isalnum():
                raise forms.ValidationError('Username can only contain letters, numbers, and underscores.')
        return username

class TelegramSettingsForm(forms.ModelForm):
    """
    Form for Telegram client settings
    """
    
    api_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Telegram API ID'
        }),
        label='API ID',
        help_text='Get this from https://my.telegram.org/apps'
    )
    
    api_hash = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Telegram API Hash'
        }),
        label='API Hash',
        help_text='Get this from https://my.telegram.org/apps'
    )
    
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        }),
        label='Phone Number',
        help_text='Your Telegram phone number with country code'
    )
    
    auto_sync_messages = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Auto-sync Messages',
        help_text='Automatically synchronize new messages',
        required=False
    )
    
    auto_sync_contacts = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Auto-sync Contacts',
        help_text='Automatically synchronize contact updates',
        required=False
    )
    
    sync_frequency = forms.ChoiceField(
        choices=[
            (60, 'Every minute'),
            (300, 'Every 5 minutes'),
            (900, 'Every 15 minutes'),
            (1800, 'Every 30 minutes'),
            (3600, 'Every hour'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Sync Frequency',
        help_text='How often to check for new messages'
    )

    class Meta:
        model = TelegramSession
        fields = [
            'phone_number', 'api_id', 'api_hash', 'auto_sync_messages',
            'auto_sync_contacts', 'sync_frequency'
        ]

    def clean_phone_number(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone_number', '').strip()
        if not phone.startswith('+'):
            raise forms.ValidationError('Phone number must include country code (e.g., +1234567890)')
        # Basic validation - should contain only digits after +
        if not phone[1:].replace(' ', '').replace('-', '').isdigit():
            raise forms.ValidationError('Invalid phone number format')
        return phone

class TelegramBotForm(forms.ModelForm):
    """
    Form for creating and managing Telegram bots
    """
    
    token = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234567890:ABCdefGHIjklMNOpqrsTUVwxyZ'
        }),
        label='Bot Token',
        help_text='Get this from @BotFather on Telegram'
    )
    
    webhook_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://yoursite.com/telegram/webhook/'
        }),
        label='Webhook URL',
        help_text='URL where Telegram will send updates (optional)',
        required=False
    )
    
    allowed_updates = forms.MultipleChoiceField(
        choices=[
            ('message', 'Messages'),
            ('edited_message', 'Edited Messages'),
            ('channel_post', 'Channel Posts'),
            ('edited_channel_post', 'Edited Channel Posts'),
            ('inline_query', 'Inline Queries'),
            ('chosen_inline_result', 'Chosen Inline Results'),
            ('callback_query', 'Callback Queries'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Allowed Update Types',
        help_text='Select which types of updates the bot should receive',
        required=False
    )

    class Meta:
        model = TelegramBot
        fields = [
            'name', 'username', 'token', 'description', 'webhook_url',
            'allowed_updates', 'is_active'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'mybotusername'
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_username(self):
        """Validate bot username"""
        username = self.cleaned_data.get('username', '').strip().lower()
        if username:
            # Remove @ if present
            username = username.lstrip('@')
            # Bot usernames must end with 'bot'
            if not username.endswith('bot'):
                raise forms.ValidationError('Bot username must end with "bot"')
        return username

    def clean_token(self):
        """Validate bot token format"""
        token = self.cleaned_data.get('token', '').strip()
        if token:
            # Basic validation for bot token format
            parts = token.split(':')
            if len(parts) != 2 or not parts[0].isdigit() or len(parts[1]) < 35:
                raise forms.ValidationError('Invalid bot token format')
        return token

class TelegramChatForm(forms.ModelForm):
    """
    Form for creating/editing Telegram chats
    """
    
    class Meta:
        model = TelegramChat
        fields = [
            'title', 'description', 'is_pinned', 'is_muted', 'is_archived'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_muted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_archived': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TelegramSearchForm(forms.Form):
    """
    Form for searching Telegram messages and chats
    """
    SEARCH_TYPE_CHOICES = [
        ('all', 'All'),
        ('messages', 'Messages'),
        ('chats', 'Chats'),
        ('contacts', 'Contacts'),
    ]
    
    query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search messages, chats, or contacts...',
            'autocomplete': 'off'
        }),
        label='Search Query',
        max_length=100
    )
    
    search_type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Search In',
        initial='all'
    )
    
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='From Date',
        required=False
    )
    
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='To Date',
        required=False
    )

class TelegramMediaForm(forms.Form):
    """
    Form for uploading media to Telegram
    """
    MEDIA_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]
    
    media_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx'
        }),
        label='Media File',
        validators=[FileExtensionValidator([
            'jpg', 'jpeg', 'png', 'gif', 'webp',
            'mp4', 'avi', 'mov', 'webm',
            'mp3', 'ogg', 'wav', 'flac',
            'pdf', 'doc', 'docx', 'txt'
        ])]
    )
    
    caption = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Optional caption...'
        }),
        label='Caption',
        max_length=1024,
        required=False
    )
    
    compress_images = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Compress Images',
        help_text='Compress images to save bandwidth',
        initial=True,
        required=False
    )

class NotificationForm(forms.ModelForm):
    """
    Form for creating and managing notifications
    """
    class Meta:
        model = Notification
        fields = [
            'title', 
            'message', 
            'notification_type', 
            'is_read', 
            'related_object_id'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notification_type': forms.Select(attrs={'class': 'form-select'}),
            'is_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'related_object_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Set the user for the notification.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Associate the notification with the current user.
        """
        notification = super().save(commit=False)
        if self.user:
            notification.user = self.user
        
        if commit:
            notification.save()
        return notification

class EmailForm(forms.ModelForm):
    """Form for composing emails for the Telebird interface"""
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        help_text="Select one or more recipients"
    )
    
    class Meta:
        model = Email
        fields = ['recipients', 'subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

class EmailSettingsForm(forms.Form):
    """
    Form for managing email client settings
    """
    THEME_CHOICES = [
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('ocean', 'Ocean Blue'),
        ('forest', 'Forest Green'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'French'),
        ('es', 'Spanish'),
        ('de', 'German'),
        ('zh', 'Chinese'),
    ]

    display_name = forms.CharField(
        label='Display Name',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your display name for emails'
        })
    )

    signature = forms.CharField(
        label='Email Signature',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Optional email signature',
            'rows': 3
        })
    )

    theme = forms.ChoiceField(
        label='Email Client Theme',
        choices=THEME_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    language = forms.ChoiceField(
        label='Language',
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean_signature(self):
        """
        Validate email signature length
        """
        signature = self.cleaned_data.get('signature', '')
        if len(signature) > 500:
            raise forms.ValidationError('Signature must be 500 characters or less.')
        return signature
