from django.db import models
from django.urls import reverse
from django.utils import timezone
from model_utils import FieldTracker
from clients.models import Client
from people.models import Person


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal Sent'),
        ('negotiation', 'In Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social', 'Social Media'),
        ('email', 'Email Campaign'),
        ('call', 'Cold Call'),
        ('event', 'Event'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Basic Information
    # Restored 'title' field for additional context
    title = models.CharField(max_length=200, default='', blank=True)
    company_name = models.CharField(max_length=200, default='')
    contact_person = models.CharField(max_length=200, default='')
    email = models.EmailField(default='')
    phone = models.CharField(max_length=20, default='')
    website = models.URLField(blank=True, null=True)
    
    # Lead Details
    description = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Status and Classification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='website')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)
    
    # Relationships
    assigned_to = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
<<<<<<< HEAD
    created_by_id = models.IntegerField(null=True, blank=True)  # Store user ID instead of ForeignKey
    modified_by_id = models.IntegerField(null=True, blank=True)  # Store user ID instead of ForeignKey
=======
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_leads')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modified_leads')
>>>>>>> d781b6071826b1e9eeb8bf33453b359a2cce4225
    converted_to_client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='converted_from_lead')
    
    # Additional Information
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    notes_text = models.TextField(blank=True)

    # Field tracker
    tracker = FieldTracker(fields=['assigned_to', 'status', 'priority', 'modified_by_id', 'next_follow_up'])

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("view_lead_dashboard", "Can view lead dashboard"),
            ("convert_lead", "Can convert lead to client"),
            ("assign_lead", "Can assign lead to user"),
        ]

    def __str__(self):
        return f"{self.company_name} - {self.contact_person}"

    def get_absolute_url(self):
        return reverse('leads:detail', args=[str(self.id)])

    def get_status_color(self):
        """Return color class based on status for consistent styling."""
        color_map = {
            'new': 'primary',
            'contacted': 'info',
            'qualified': 'success',
            'proposal': 'warning',
            'negotiation': 'danger',
            'won': 'success',
            'lost': 'danger',
        }
        return color_map.get(self.status, 'secondary')

    def get_priority_color(self):
        """Return Bootstrap color class based on priority."""
        color_map = {
            'low': 'secondary',
            'medium': 'info',
            'high': 'warning',
            'urgent': 'danger',
        }
        return color_map.get(self.priority, 'secondary')

    def convert_to_client(self):
        if not self.converted_to_client:
            client = Client.objects.create(
                name=self.company_name,
                contact_person=self.contact_person,
                email=self.email,
                phone=self.phone,
                notes=self.notes_text
            )
            self.converted_to_client = client
            self.status = 'won'
            self.save()
            return client
        return self.converted_to_client

class LeadActivity(models.Model):
    ACTIVITY_TYPES = [
        ('created', 'Created'),
        ('status_change', 'Status Change'),
        ('assignment', 'Assignment'),
        ('note', 'Note'),
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('task', 'Task'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_id = models.IntegerField(null=True, blank=True)  # Store user ID instead of ForeignKey
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Lead activities'

    def __str__(self):
        return f"{self.lead.company_name} - {self.activity_type} - {self.created_at.date()}"

    def get_activity_type_icon(self):
        """Return Font Awesome icon class based on activity type."""
        icon_map = {
            'created': 'plus',
            'status_change': 'exchange-alt',
            'assignment': 'user-plus',
            'note': 'sticky-note',
            'call': 'phone',
            'email': 'envelope',
            'meeting': 'handshake',
            'task': 'tasks',
        }
        return icon_map.get(self.activity_type, 'circle')

class LeadNote(models.Model):
    """Model for lead notes"""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_by_id = models.IntegerField(null=True, blank=True)  # Store user ID instead of ForeignKey
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.lead.company_name} - {self.created_at.date()}"

class LeadDocument(models.Model):
    """Model for lead documents/attachments"""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='leads/documents/%Y/%m/')
    description = models.TextField(blank=True, null=True)
    created_by_id = models.IntegerField(null=True, blank=True)  # Store user ID instead of ForeignKey
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file.name} - {self.lead.company_name}"

    def get_file_extension(self):
        """Return the file extension"""
        return self.file.name.split('.')[-1].lower() if '.' in self.file.name else ''

    def get_file_icon(self):
        """Return Font Awesome icon class based on file type"""
        ext = self.get_file_extension()
        icon_map = {
            'pdf': 'file-pdf',
            'doc': 'file-word',
            'docx': 'file-word',
            'xls': 'file-excel',
            'xlsx': 'file-excel',
            'ppt': 'file-powerpoint',
            'pptx': 'file-powerpoint',
            'jpg': 'file-image',
            'jpeg': 'file-image',
            'png': 'file-image',
            'gif': 'file-image',
            'txt': 'file-alt',
            'zip': 'file-archive',
            'rar': 'file-archive',
        }
        return f"fa-{icon_map.get(ext, 'file')}"
