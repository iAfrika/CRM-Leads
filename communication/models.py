from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import uuid
from datetime import timedelta

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    relativedelta = None

# Create your models here.

class Contact(models.Model):
    """Contacts model for storing contact information"""
    MESSENGER_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('signal', 'Signal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Messenger details
    messenger_type = models.CharField(max_length=20, choices=MESSENGER_CHOICES, blank=True, null=True)
    messenger_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional details
    company = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}"

class EmailAccount(models.Model):
    """Email account configuration model"""
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('telebird', 'Telebird'),
        ('yahoo', 'Yahoo'),
        ('custom', 'Custom SMTP'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_accounts')
    email = models.EmailField(unique=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    
    # SMTP and IMAP settings
    smtp_host = models.CharField(max_length=255)
    smtp_port = models.IntegerField(default=587)
    imap_host = models.CharField(max_length=255)
    imap_port = models.IntegerField(default=993)
    
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Encrypted in production
    
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.email

class EmailAttachment(models.Model):
    """Model to store email attachments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(
        upload_to='email_attachments/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'png', 'txt', 'xlsx'])]
    )
    filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name.split('/')[-1]
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return self.filename or self.file.name

class Email(models.Model):
    """Email message model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_emails'
    )
    
    # For compatibility with the Telebird views, add these fields
    sender_name = models.CharField(max_length=255, blank=True)
    sender_email = models.EmailField(blank=True)
    
    # Replace single recipient with ManyToMany relationship
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='received_emails',
        blank=True
    )
    
    # Add CC field
    cc = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='cc_emails',
        blank=True
    )
    
    subject = models.CharField(max_length=200)
    body = models.TextField()
    
    sent_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_read = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    attachments = models.ManyToManyField(
        EmailAttachment, 
        related_name='emails', 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.subject

class Event(models.Model):
    """Calendar event model with enhanced scheduling capabilities"""
    RECURRENCE_CHOICES = [
        ('none', 'No Repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('shared', 'Shared'),
    ]
    
    CATEGORY_CHOICES = [
        ('meeting', 'Meeting'),
        ('task', 'Task'),
        ('appointment', 'Appointment'),
        ('reminder', 'Reminder'),
        ('birthday', 'Birthday'),
        ('holiday', 'Holiday'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    
    # Add attendees field
    attendees = models.ManyToManyField(Contact, related_name='attended_events', blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    location = models.CharField(max_length=300, blank=True, null=True)
    
    # Enhanced categorization and privacy
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='private')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Color coding for better visualization
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code for event display')
    
    # Recurrence settings
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='none')
    recurrence_interval = models.IntegerField(default=1)  # Every X days/weeks/months/years
    recurrence_end_date = models.DateField(null=True, blank=True)  # Optional end date for recurring events
    
    # Advanced notification settings
    send_email_reminder = models.BooleanField(default=True)
    send_sms_reminder = models.BooleanField(default=False)
    send_whatsapp_reminder = models.BooleanField(default=False)
    
    reminder_times = models.JSONField(
        default=list, 
        blank=True, 
        help_text='List of reminder times before the event (in minutes)'
    )
    
    # Attendees and sharing
    invited_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='invited_events')
    
    # External links or video conference details
    video_conference_link = models.URLField(blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def is_recurring(self):
        """Check if the event is a recurring event."""
        return self.recurrence_type != 'none'
    
    def get_next_occurrence(self):
        """Calculate the next occurrence of a recurring event."""
        if not self.is_recurring():
            return None
        
        # Implement logic to calculate next occurrence based on recurrence type
        # This is a placeholder and would need more complex implementation
        if relativedelta is None:
            # Fallback to basic timedelta if dateutil is not available
            if self.recurrence_type == 'daily':
                return self.start_time + timedelta(days=self.recurrence_interval)
            elif self.recurrence_type == 'weekly':
                return self.start_time + timedelta(weeks=self.recurrence_interval)
            else:
                return self.start_time + timedelta(days=30 * self.recurrence_interval)
        else:
            if self.recurrence_type == 'daily':
                return self.start_time + timedelta(days=self.recurrence_interval)
            elif self.recurrence_type == 'weekly':
                return self.start_time + timedelta(weeks=self.recurrence_interval)
            elif self.recurrence_type == 'monthly':
                return self.start_time + relativedelta(months=self.recurrence_interval)
            elif self.recurrence_type == 'yearly':
                return self.start_time + relativedelta(years=self.recurrence_interval)
        
        return None

class Notification(models.Model):
    """Notification model for events and emails"""
    NOTIFICATION_TYPES = [
        ('event_reminder', 'Event Reminder'),
        ('email', 'Email'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    is_read = models.BooleanField(default=False)
    related_object_id = models.UUIDField(null=True, blank=True)  # Link to Event or Email
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class WhatsAppMessage(models.Model):
    """WhatsApp messaging model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='whatsapp_messages')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='whatsapp_messages')
    
    message_text = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Optional media attachments
    media_file = models.FileField(
        upload_to='whatsapp_media/%Y/%m/%d/',
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'])]
    )
    
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"WhatsApp Message to {self.contact.first_name} - {self.sent_at}"

class TelegramContact(models.Model):
    """Enhanced Telegram contact model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_contacts')
    
    # Telegram specific fields
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Status and verification
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)
    is_contact = models.BooleanField(default=False)
    is_mutual_contact = models.BooleanField(default=False)
    
    # Additional info
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='telegram_profiles/', blank=True, null=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Telegram Contact"
        verbose_name_plural = "Telegram Contacts"
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} (@{self.username or self.telegram_id})"
    
    @property
    def display_name(self):
        """Get the display name for the contact."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        else:
            return f"User {self.telegram_id}"

class TelegramChat(models.Model):
    """Telegram chat model for groups and channels"""
    CHAT_TYPES = [
        ('private', 'Private'),
        ('group', 'Group'),
        ('supergroup', 'Supergroup'),
        ('channel', 'Channel'),
        ('bot', 'Bot'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_chats')
    
    # Telegram specific fields
    telegram_chat_id = models.BigIntegerField()
    chat_type = models.CharField(max_length=20, choices=CHAT_TYPES)
    title = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Participants (for private chats, link to TelegramContact)
    contact = models.ForeignKey(TelegramContact, on_delete=models.CASCADE, null=True, blank=True, related_name='chats')
    
    # Chat settings
    is_pinned = models.BooleanField(default=False)
    is_muted = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    unread_count = models.IntegerField(default=0)
    
    # Media
    photo = models.ImageField(upload_to='telegram_chat_photos/', blank=True, null=True)
    
    # Last activity
    last_message_date = models.DateTimeField(null=True, blank=True)
    last_read_message_id = models.BigIntegerField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Telegram Chat"
        verbose_name_plural = "Telegram Chats"
        unique_together = ['user', 'telegram_chat_id']
        ordering = ['-last_message_date']
    
    def __str__(self):
        if self.chat_type == 'private' and self.contact:
            return f"Chat with {self.contact.display_name}"
        elif self.title:
            return self.title
        else:
            return f"Chat {self.telegram_chat_id}"

class TelegramMessage(models.Model):
    """Enhanced Telegram messaging model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('voice', 'Voice Message'),
        ('sticker', 'Sticker'),
        ('animation', 'Animation/GIF'),
        ('location', 'Location'),
        ('contact', 'Contact'),
        ('poll', 'Poll'),
        ('venue', 'Venue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_messages')
    
    # Chat and contact relationships
    chat = models.ForeignKey(TelegramChat, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    contact = models.ForeignKey(TelegramContact, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    
    # Telegram specific fields
    telegram_message_id = models.BigIntegerField(null=True, blank=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    
    # Message content
    message_text = models.TextField(blank=True, null=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Message properties
    is_outgoing = models.BooleanField(default=False)  # True if sent by the user
    is_forwarded = models.BooleanField(default=False)
    is_reply = models.BooleanField(default=False)
    reply_to_message_id = models.BigIntegerField(null=True, blank=True)
    forward_from_chat_id = models.BigIntegerField(null=True, blank=True)
    forward_from_message_id = models.BigIntegerField(null=True, blank=True)
    
    # Status and delivery
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_edited = models.BooleanField(default=False)
    edit_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    # Media attachments
    media_file = models.FileField(
        upload_to='telegram_media/%Y/%m/%d/',
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'mp4', 'mp3', 'ogg', 'webm'])]
    )
    media_caption = models.TextField(blank=True, null=True)
    media_type = models.CharField(max_length=20, blank=True, null=True)
    media_size = models.IntegerField(null=True, blank=True)  # File size in bytes
    media_duration = models.IntegerField(null=True, blank=True)  # Duration for audio/video
    
    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Message reactions and interactions
    reactions = models.JSONField(default=dict, blank=True)  # Store reaction data
    views = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Telegram Message"
        verbose_name_plural = "Telegram Messages"
        unique_together = ['telegram_message_id', 'telegram_chat_id']
        ordering = ['-sent_at', '-created_at']
        indexes = [
            models.Index(fields=['telegram_chat_id', '-sent_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['is_outgoing', 'chat']),
        ]
    
    def __str__(self):
        if self.contact:
            direction = "to" if self.is_outgoing else "from"
            return f"Message {direction} {self.contact.display_name} - {self.sent_at or self.created_at}"
        else:
            return f"Message in {self.chat} - {self.sent_at or self.created_at}"
    
    @property
    def preview_text(self):
        """Get a preview of the message text."""
        if self.message_text:
            return self.message_text[:100] + ('...' if len(self.message_text) > 100 else '')
        elif self.message_type != 'text':
            return f"[{self.get_message_type_display()}]"
        else:
            return "[No content]"
    
    def mark_as_read(self):
        """Mark the message as read."""
        if self.status != 'read':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at', 'updated_at'])

class TelegramSession(models.Model):
    """Store Telegram session data for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_session')
    
    # Telegram credentials
    phone_number = models.CharField(max_length=20)
    session_string = models.TextField(blank=True, null=True)  # Encrypted session data
    api_id = models.CharField(max_length=20, blank=True, null=True)
    api_hash = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_authenticated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Settings
    auto_sync_messages = models.BooleanField(default=True)
    auto_sync_contacts = models.BooleanField(default=True)
    sync_frequency = models.IntegerField(default=300)  # Sync every 5 minutes
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Telegram Session"
        verbose_name_plural = "Telegram Sessions"
    
    def __str__(self):
        return f"Telegram session for {self.user.username} ({self.phone_number})"

class TelegramBot(models.Model):
    """Store Telegram bot configurations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_bots')
    
    # Bot details
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    token = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Bot settings
    is_active = models.BooleanField(default=True)
    webhook_url = models.URLField(blank=True, null=True)
    allowed_updates = models.JSONField(default=list, blank=True)
    
    # Statistics
    total_messages_sent = models.IntegerField(default=0)
    total_messages_received = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Telegram Bot"
        verbose_name_plural = "Telegram Bots"
        unique_together = ['user', 'username']
    
    def __str__(self):
        return f"Bot @{self.username} ({self.name})"

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    
    # Email preferences
    EMAIL_INTERFACE_CHOICES = [
        ('basic', 'Basic'),
        ('telebird', 'Telebird'),
    ]
    
    default_email_interface = models.CharField(
        max_length=20,
        choices=EMAIL_INTERFACE_CHOICES,
        default='basic'
    )
