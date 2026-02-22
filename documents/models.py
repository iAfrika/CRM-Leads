import pdfkit
from django.db import models
from django.urls import reverse
from clients.models import Client
from .utils import generate_quote_pdf
from django.core.files import File
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta

class Document(models.Model):
    DOCUMENT_TYPES = (
        ('QUOTE', 'Quote'),
        ('INVOICE', 'Invoice'),
        ('RECEIPT', 'Receipt'),
        ('DELIVERY_NOTE', 'Delivery Note'),
        ('PROFORMA_INVOICE', 'Proforma Invoice'),
        ('PAYMENT_RECEIPT', 'Payment Receipt'),
        ('SALES_RECEIPT', 'Sales Receipt'),
        ('PURCHASE', 'Purchase'),
        ('EXPENSE', 'Expense'),
        ('SALE', 'Sale'),
    )

    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
        ('INVOICED', 'Invoiced'),
    )

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    description = models.TextField(blank=True)
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    
    # Financial information
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    apply_vat = models.BooleanField(default=True, verbose_name='Apply VAT')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Document information
    document_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    
    # Relationships
    quote = models.ForeignKey('Quote', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    expense = models.ForeignKey('expenses.Expense', on_delete=models.SET_NULL, null=True, blank=True, related_name='document')
    purchase = models.ForeignKey('purchases.Purchase', on_delete=models.SET_NULL, null=True, blank=True, related_name='document')
    sale = models.ForeignKey('sales.Sale', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_id = models.IntegerField(null=True, blank=True, help_text='User ID who created this document')
    updated_by_id = models.IntegerField(null=True, blank=True, help_text='User ID who last updated this document')

    # Add number fields for different document types
    quote_number = models.IntegerField(null=True, blank=True)
    receipt_number = models.IntegerField(null=True, blank=True)
    
    # Edit tracking
    edit_count = models.IntegerField(default=0)

    def calculate_subtotal(self):
        """Calculate subtotal based on document type"""
        if self.document_type == 'QUOTE' and self.quote:
            return self.quote.total_amount
        elif self.document_type == 'INVOICE':
            return sum(item.total for item in self.items.all())
        return self.total_amount / (1 + self.tax_rate/100) if self.total_amount else 0

    def calculate_tax(self):
        """Calculate tax amount"""
        if not self.subtotal:
            self.subtotal = self.calculate_subtotal()
        if self.apply_vat:
            return self.subtotal * (self.tax_rate/100)
        return 0

    def save(self, *args, **kwargs):
        if not self.id:
            # If this is a new document
            if self.document_type == 'QUOTE':
                # Get the last quote number
                last_quote = Document.objects.filter(document_type='QUOTE').order_by('-quote_number').first()
                self.quote_number = (last_quote.quote_number or 0) + 1 if last_quote else 1
            elif self.document_type in ['RECEIPT', 'SALES_RECEIPT']:
                # Get the last receipt number
                last_receipt = Document.objects.filter(
                    document_type__in=['RECEIPT', 'SALES_RECEIPT'],
                    receipt_number__isnull=False
                ).order_by('-receipt_number').first()
                
                # Safely get the next receipt number
                if last_receipt and last_receipt.receipt_number is not None:
                    self.receipt_number = last_receipt.receipt_number + 1
                else:
                    self.receipt_number = 1

        # Calculate subtotal if not set
        if not self.subtotal:
            self.subtotal = self.calculate_subtotal()
        
        # Calculate tax if not set
        if not self.tax_amount:
            self.tax_amount = self.calculate_tax()
        
        # Calculate total if not set
        if not self.total_amount:
            self.total_amount = self.subtotal + self.tax_amount

        super().save(*args, **kwargs)
    
    def increment_edit_count(self):
        """Increment the edit count without triggering the full save logic"""
        self.edit_count += 1
        Document.objects.filter(id=self.id).update(edit_count=self.edit_count)

    def get_document_number(self):
        """Return the appropriate document number based on type"""
        if self.document_type == 'INVOICE':
            return self.invoice_number
        elif self.document_type == 'QUOTE':
            return f"Q{self.quote_number:04d}" if self.quote_number else None
        elif self.document_type in ['RECEIPT', 'SALES_RECEIPT']:
            return f"R{self.receipt_number:04d}" if self.receipt_number else None
        return None

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.client.name if self.client else 'No Client'}"

    def get_absolute_url(self):
        return reverse('documents:document_detail', args=[str(self.id)])

    def clean(self):
        """Validate the document"""
        from django.core.exceptions import ValidationError
        
        if self.document_type == 'INVOICE' and not self.due_date:
            raise ValidationError({'due_date': 'Due date is required for invoices'})
        
        if self.due_date and self.due_date < self.document_date:
            raise ValidationError({'due_date': 'Due date cannot be earlier than document date'})

    def mark_as_sent(self):
        """Mark document as sent"""
        if self.status == 'DRAFT':
            self.status = 'SENT'
            self.save()
        else:
            raise ValueError(f"Cannot mark as sent: document is {self.status}")

    def mark_as_paid(self):
        """Mark document as paid"""
        if self.status in ['SENT', 'OVERDUE']:
            self.status = 'PAID'
            self.save()
        else:
            raise ValueError(f"Cannot mark as paid: document is {self.status}")

    def mark_overdue_documents():
        """Mark all overdue documents as overdue"""
        overdue_documents = Document.objects.filter(
            status__in=['SENT', 'OVERDUE'],
            due_date__lt=timezone.now().date()
        )
        
        for doc in overdue_documents:
            doc.status = 'OVERDUE'
            doc.save()
        
        return len(overdue_documents)

    def is_overdue(self):
        """Check if the document is overdue"""
        return self.status in ['SENT', 'OVERDUE'] and self.due_date < timezone.now().date()

    def generate_pdf(self):
        # Create a BytesIO buffer for the PDF
        buffer = BytesIO()
        
        # Create the PDF object, using the BytesIO object as its "file."
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Draw things on the PDF
        p.drawString(100, 750, f"Document #{self.pk}")
        # ... add more content as needed ...
        
        # Close the PDF object cleanly
        p.showPage()
        p.save()
        
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

class Quote(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('INVOICED', 'Invoiced'),
    )
    
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    quote_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    apply_vat = models.BooleanField(default=True, verbose_name='Apply VAT')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    valid_until = models.DateField()
    terms = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_file = models.FileField(upload_to='quotes/', blank=True, null=True)
    
    # Edit tracking
    edit_count = models.IntegerField(default=0)

    def create_document(self):
        """Create a Document instance from this Quote"""
        return Document.objects.create(
            client=self.client,
            document_type='QUOTE',
            description=self.description,
            subtotal=self.subtotal,
            tax_rate=self.tax_rate,
            tax_amount=self.tax_amount,
            total_amount=self.total_amount,
            document_date=self.created_at.date(),
            status='DRAFT',
            quote=self
        )

    def convert_to_invoice(self):
        """Convert this quote to an invoice"""
        if self.status not in ['DRAFT', 'SENT', 'ACCEPTED']:
            raise ValueError(f"Only draft, sent or accepted quotes can be converted to invoices. Current status: {self.status}")
        
        if Document.objects.filter(quote=self, document_type='INVOICE').exists():
            raise ValueError("This quote has already been converted to an invoice")
        
        # Generate invoice number in same pattern as quote: I + CompanyInitials + 0001
        from registration.models import Company, CompanyUser
        from django.conf import settings
        import re
        
        # Get company initials from current context
        company_initials = 'CC'
        try:
            # Try to get company from database settings
            company_db = getattr(settings, 'COMPANY_DATABASE', 'default')
            if company_db != 'default':
                # Extract company from database name
                companies = Company.objects.using('default').all()
                for company in companies:
                    if company.database_name == company_db and company.initials:
                        company_initials = company.initials
                        break
        except:
            pass
        
        # Find highest existing invoice number
        highest_num = 0
        for doc in Document.objects.filter(document_type='INVOICE'):
            if doc.invoice_number:
                numbers = re.findall(r'\d+', doc.invoice_number)
                if numbers:
                    num = int(numbers[-1])
                    if num > highest_num:
                        highest_num = num
        
        seq_num = highest_num + 1
        invoice_number = f'INV{company_initials}{seq_num:04d}'
        
        document = Document.objects.create(
            client=self.client,
            document_type='INVOICE',
            invoice_number=invoice_number,
            description=self.description,
            subtotal=self.subtotal,
            apply_vat=self.apply_vat,
            tax_rate=self.tax_rate,
            tax_amount=self.tax_amount,
            total_amount=self.total_amount,
            document_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            status='DRAFT',
            quote=self
        )
        
        # Copy items
        for item in self.items.all():
            total = item.quantity * item.unit_price * (1 - item.discount/100)
            InvoiceItem.objects.create(
                invoice=document,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total=total
            )
        
        # Update quote status to INVOICED
        self.status = 'INVOICED'
        self.save()
        
        # Also update the related Document status if it exists
        if hasattr(self, 'documents') and self.documents.exists():
            quote_doc = self.documents.filter(document_type='QUOTE').first()
            if quote_doc:
                quote_doc.status = 'INVOICED'
                quote_doc.save()
        
        return document

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'

    def __str__(self):
        return f"Quote #{self.quote_number} - {self.client.name}"

    def get_absolute_url(self):
        return reverse('documents:quote_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Calculate tax amount and total if not set
        if self.tax_rate and self.subtotal:
            self.tax_amount = self.subtotal * (self.tax_rate / 100)
            self.total_amount = self.subtotal + self.tax_amount
        super().save(*args, **kwargs)

    def generate_pdf(self):
        # Get company information from request context or database
        from registration.models import Company, CompanyUser
        from django.contrib.auth.models import User
        
        # Try to get company from the user who created the quote
        company = None
        if hasattr(self, 'created_by') and self.created_by:
            company_user = CompanyUser.objects.filter(user=self.created_by).first()
            if company_user:
                company = company_user.company
        
        # Fallback to first company if not found
        if not company:
            company = Company.objects.first()
        
        # Prepare company data
        company_data = {
            'company_name': company.name if company else 'Your Company Name',
            'company_address': company.physical_address if company else 'Your Company Address',
            'company_phone': company.phone_number if company else 'Your Company Phone',
            'company_email': company.email if company else 'your@email.com',
            'company_logo': company.logo.url if (company and company.logo) else None,
            'company_initials': company.initials if company else '',
        }
        
        # Render the quote template to HTML
        html_content = render_to_string('documents/quote_pdf.html', {
            'quote': self,
            **company_data
        })
        
        # Generate PDF from HTML
        pdf_filename = f'quote_{self.quote_number}.pdf'
        pdf_path = os.path.join('quotes', pdf_filename)
        
        # Configure pdfkit options
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
            'enable-local-file-access': None,  # Allow loading local images
        }
        
        # Generate PDF
        pdf_content = pdfkit.from_string(html_content, False, options=options)
        
        # Save PDF to FileField
        if self.pdf_file:
            self.pdf_file.delete()
        
        self.pdf_file.save(pdf_filename, ContentFile(pdf_content), save=True)
        
        return self.pdf_file

class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def get_total(self):
        return self.quantity * self.unit_price * (1 - self.discount/100)

    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"

class Expenditure(models.Model):
    CATEGORY_CHOICES = [
        ('SUPPLIES', 'Office Supplies'),
        ('EQUIPMENT', 'Equipment'),
        ('UTILITIES', 'Utilities'),
        ('RENT', 'Rent'),
        ('SALARY', 'Salary'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()
    receipt = models.FileField(upload_to='expenditure_receipts/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - ${self.amount}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Document, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"
