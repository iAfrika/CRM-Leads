from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.validators import EmailValidator
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_by_id = models.IntegerField(null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('discontinued', 'Discontinued'),
        ('out_of_stock', 'Out of Stock'),
    )
    
    item_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by_id = models.IntegerField(null=True)
    updated_by_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.item_code} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Generate a unique item code if not provided
        if not self.item_code:
            self.item_code = f"PROD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def profit_margin(self):
        """Calculate the profit margin percentage"""
        if self.buying_price > 0:
            return ((self.selling_price - self.buying_price) / self.buying_price) * 100
        return 0
    
    @property
    def is_low_stock(self):
        """Check if the product is low on stock"""
        return self.current_stock <= self.reorder_level

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Calculate total amount if not provided
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_price
        
        # Update product stock based on transaction type
        if self.pk is None:  # Only for new transactions
            if self.transaction_type == 'purchase' or self.transaction_type == 'return':
                self.product.current_stock += self.quantity
            elif self.transaction_type == 'sale':
                self.product.current_stock -= self.quantity
            elif self.transaction_type == 'adjustment':
                # For adjustments, quantity can be positive or negative
                self.product.current_stock += self.quantity
            
            self.product.save()
        
        super().save(*args, **kwargs)

class Purchase(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    )
    
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='product_purchases')
    purchase_date = models.DateField(default=timezone.now)
    reference_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    created_by_id = models.IntegerField(null=True)
    updated_by_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"PO-{self.reference_number}"
    
    def save(self, *args, **kwargs):
        # Generate a reference number if not provided
        if not self.reference_number:
            self.reference_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"
    
    def save(self, *args, **kwargs):
        # Calculate total amount if not provided
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Sale(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField(blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    sale_date = models.DateField(default=timezone.now)
    reference_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    created_by_id = models.IntegerField(null=True)
    updated_by_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-sale_date']
    
    def __str__(self):
        return f"SO-{self.reference_number}"
    
    def save(self, *args, **kwargs):
        # Generate a reference number if not provided
        if not self.reference_number:
            self.reference_number = f"SO-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sale_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Calculate total price if not provided
        if not self.total_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )
    
    user_id = models.IntegerField(null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=200)
    changes = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} {self.model_name} - {self.object_repr} by {self.user}"
