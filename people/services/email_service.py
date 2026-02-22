from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    def send_email(self, subject, message, recipient_email):
        """
        Send an email to a recipient
        
        Args:
            subject (str): Email subject
            message (str): Email body
            recipient_email (str): Recipient's email address
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Get the sender email from settings or use a default
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            
            # Send the email
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True, None
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False, str(e)
