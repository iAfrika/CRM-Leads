import logging
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.from_email = settings.EMAIL_HOST_USER

    def send_email(self, subject, message, recipient_email):
        """Send email to a list of recipients"""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[recipient_email]
                fail_silently=False,
            )

            return True, "Email sent successfully"
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False, str(e)
            
            
