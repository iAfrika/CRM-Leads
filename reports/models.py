from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import datetime, timedelta
import calendar

User = get_user_model()


class Report(models.Model):
    """
    Model for storing report metadata.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    shared_with = models.ManyToManyField(User, related_name='shared_reports', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def to_dict(self, include_charts=True, include_data_tables=True, include_metadata=True):
        """
        Convert the report to a dictionary for export.
        """
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }
        
        if include_metadata:
            data.update({
                'created_by': self.created_by.username,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
            })
        
        if hasattr(self, 'configuration'):
            config = self.configuration
            data.update({
                'report_type': config.report_type,
                'time_range': config.time_range,
                'chart_type': config.chart_type,
                'filters': config.filters,
            })
            
        return data


class ReportConfiguration(models.Model):
    """
    Model for storing report configuration.
    """
    REPORT_TYPES = [
        ('BANKING', 'Banking'),
        ('SALES', 'Sales'),
        ('EXPENSES', 'Expenses'),
        ('CLIENTS', 'Clients'),
        ('LEADS', 'Leads'),
        ('CUSTOM', 'Custom'),
    ]
    
    TIME_RANGES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
        ('CUSTOM', 'Custom Range'),
    ]
    
    CHART_TYPES = [
        ('BAR', 'Bar Chart'),
        ('LINE', 'Line Chart'),
        ('PIE', 'Pie Chart'),
        ('DOUGHNUT', 'Doughnut Chart'),
        ('RADAR', 'Radar Chart'),
        ('POLAR', 'Polar Area Chart'),
        ('TABLE', 'Data Table'),
    ]
    
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='configuration')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    time_range = models.CharField(max_length=20, choices=TIME_RANGES, default='MONTHLY')
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, default='BAR')
    filters = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    is_favorite = models.BooleanField(default=False)
    custom_colors = models.JSONField(default=dict, encoder=DjangoJSONEncoder, blank=True)
    date_field = models.CharField(max_length=50, blank=True)
    group_by = models.CharField(max_length=50, blank=True)
    aggregate_function = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.report.name} - {self.get_report_type_display()}"


class ReportSchedule(models.Model):
    """
    Model for scheduling report deliveries.
    """
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
    ]
    
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    FORMAT_CHOICES = [
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='schedules')
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    day_of_week = models.IntegerField(choices=DAY_CHOICES, null=True, blank=True)
    day_of_month = models.IntegerField(null=True, blank=True)
    time_of_day = models.TimeField()
    recipients = models.TextField(help_text="Comma-separated list of email addresses")
    subject = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    format = models.CharField(max_length=5, choices=FORMAT_CHOICES, default='PDF')
    is_active = models.BooleanField(default=True)
    next_run = models.DateTimeField()
    last_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.report.name} - {self.get_frequency_display()}"
    
    def calculate_next_run(self):
        """
        Calculate the next run time based on frequency.
        """
        now = timezone.now()
        
        if self.frequency == 'DAILY':
            # Next day at specified time
            next_date = now.date() + timedelta(days=1)
            next_time = self.time_of_day
            self.next_run = datetime.combine(next_date, next_time, tzinfo=now.tzinfo)
        
        elif self.frequency == 'WEEKLY':
            # Next occurrence of the specified day of week
            days_ahead = self.day_of_week - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_date = now.date() + timedelta(days=days_ahead)
            next_time = self.time_of_day
            self.next_run = datetime.combine(next_date, next_time, tzinfo=now.tzinfo)
        
        elif self.frequency == 'MONTHLY':
            # Next month on the specified day
            if now.day >= self.day_of_month:  # This month's day has passed
                if now.month == 12:
                    next_month = 1
                    next_year = now.year + 1
                else:
                    next_month = now.month + 1
                    next_year = now.year
            else:
                next_month = now.month
                next_year = now.year
            
            # Handle month lengths
            last_day = calendar.monthrange(next_year, next_month)[1]
            day = min(self.day_of_month, last_day)
            
            next_date = datetime(next_year, next_month, day).date()
            next_time = self.time_of_day
            self.next_run = datetime.combine(next_date, next_time, tzinfo=now.tzinfo)
        
        elif self.frequency == 'QUARTERLY':
            # Next quarter on the specified day
            month = now.month
            quarter = (month - 1) // 3 + 1
            next_quarter = quarter + 1 if quarter < 4 else 1
            next_year = now.year if next_quarter > quarter else now.year + 1
            next_month = (next_quarter - 1) * 3 + 1  # First month of next quarter
            
            # Handle month lengths
            last_day = calendar.monthrange(next_year, next_month)[1]
            day = min(self.day_of_month or 1, last_day)
            
            next_date = datetime(next_year, next_month, day).date()
            next_time = self.time_of_day
            self.next_run = datetime.combine(next_date, next_time, tzinfo=now.tzinfo)
        
        return self.next_run


class ReportDelivery(models.Model):
    """
    Model for tracking report deliveries.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]
    
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.CASCADE, related_name='deliveries')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField(null=True, blank=True)
    recipients = models.TextField(blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    format = models.CharField(max_length=5, blank=True)
    file_path = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.schedule.report.name} - {self.sent_at or 'Pending'}"


class DataSource(models.Model):
    """
    Model for external data sources.
    """
    SOURCE_TYPES = [
        ('DATABASE', 'Database'),
        ('API', 'API'),
        ('CSV', 'CSV File'),
    ]
    
    API_FORMATS = [
        ('JSON', 'JSON'),
        ('XML', 'XML'),
    ]
    
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_sources')
    
    # Database connection fields
    connection_string = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)
    
    # API connection fields
    api_url = models.URLField(blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    api_format = models.CharField(max_length=10, choices=API_FORMATS, blank=True)
    
    # File connection fields
    file_path = models.CharField(max_length=255, blank=True)
    has_header = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class UserPermission(models.Model):
    """
    Model for user permissions on reports.
    """
    ROLE_CHOICES = [
        ('VIEWER', 'Viewer'),
        ('EDITOR', 'Editor'),
        ('ADMIN', 'Admin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_permissions')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='VIEWER')
    can_create = models.BooleanField(default=False)
    can_schedule = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'created_by')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class ReportSettings(models.Model):
    """
    Model for user-specific report settings.
    """
    COLOR_SCHEMES = [
        ('DEFAULT', 'Default'),
        ('PASTEL', 'Pastel'),
        ('VIBRANT', 'Vibrant'),
        ('MONOCHROME', 'Monochrome'),
        ('CUSTOM', 'Custom'),
    ]
    
    LEGEND_POSITIONS = [
        ('TOP', 'Top'),
        ('RIGHT', 'Right'),
        ('BOTTOM', 'Bottom'),
        ('LEFT', 'Left'),
    ]
    
    ACCESS_CHOICES = [
        ('PRIVATE', 'Private'),
        ('TEAM', 'Team'),
        ('PUBLIC', 'Public'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='report_settings')
    default_time_range = models.CharField(max_length=20, choices=ReportConfiguration.TIME_RANGES, default='MONTHLY')
    default_chart_type = models.CharField(max_length=20, choices=ReportConfiguration.CHART_TYPES, default='BAR')
    reports_per_page = models.IntegerField(default=10)
    enable_caching = models.BooleanField(default=True)
    cache_timeout = models.IntegerField(default=3600)  # in seconds
    color_scheme = models.CharField(max_length=20, choices=COLOR_SCHEMES, default='DEFAULT')
    chart_font = models.CharField(max_length=50, default='Arial')
    chart_title_size = models.IntegerField(default=18)
    chart_label_size = models.IntegerField(default=14)
    show_grid_lines = models.BooleanField(default=True)
    show_legends = models.BooleanField(default=True)
    legend_position = models.CharField(max_length=10, choices=LEGEND_POSITIONS, default='RIGHT')
    default_report_access = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='PRIVATE')
    allow_report_sharing = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Settings for {self.user.username}"
