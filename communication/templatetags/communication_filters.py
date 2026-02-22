"""
Custom template filters for the communication app
"""
import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """
    Extract the filename from a file path.
    Usage: {{ file.name|basename }}
    """
    if value:
        return os.path.basename(str(value))
    return ''

@register.filter
def filesize(value):
    """
    Format file size in human readable format.
    Usage: {{ file.size|filesize }}
    """
    if not value:
        return '0 bytes'
    
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if value < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TB"

@register.filter
def truncate_filename(value, length=30):
    """
    Truncate filename if too long, keeping extension.
    Usage: {{ file.name|truncate_filename:25 }}
    """
    if not value:
        return ''
    
    filename = os.path.basename(str(value))
    if len(filename) <= length:
        return filename
    
    name, ext = os.path.splitext(filename)
    if len(ext) >= length - 3:
        return filename[:length] + '...'
    
    truncated_name = name[:length - len(ext) - 3]
    return f"{truncated_name}...{ext}"
