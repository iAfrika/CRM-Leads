from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class PurchaseCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by_id = models.IntegerField(null=True)
    profile_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Purchase Categories"
    
    def __str__(self):
        return self.name

class Purchase(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Credit/Debit Card'),
        ('CHEQUE', 'Cheque'),
        ('MPESA', 'M-Pesa'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.ForeignKey(
        PurchaseCategory, 
        on_delete=models.SET_NULL,
        null=True
    )
    project = models.ForeignKey(
        'project_management.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases'
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    vendor = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        default='CASH'
    )
    description = models.TextField(blank=True)
    invoice = models.FileField(
        upload_to='purchases/invoices/%Y/%m/',
        blank=True,
        null=True
    )
    created_by_id = models.IntegerField(null=True)
    profile_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.amount} ({self.date})"
    
    def save(self, *args, **kwargs):
        # Update amount based on quantity and unit price
        self.amount = self.quantity * self.unit_price
        super(Purchase, self).save(*args, **kwargs)

    def create_document(self):
        """Create a Document instance from this Purchase"""
        from decimal import Decimal
        from documents.models import Document
        from clients.models import Client
        
        # Try to get a default client or create a generic one if not found
        try:
            default_client = Client.objects.first() or Client.objects.create(
                name='Default Client', 
                email='default@example.com'
            )
        except Exception:
            default_client = None

        return Document.objects.create(
            client=default_client,
            document_type='PURCHASE',
            description=self.title,
            subtotal=self.amount,
            tax_rate=Decimal('0.00'),
            tax_amount=Decimal('0.00'),
            total_amount=self.amount,
            document_date=self.date,
            status='COMPLETED',
            purchase=self
        )
