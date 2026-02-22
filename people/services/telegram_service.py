import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    """Service for sending Telegram messages"""
    
    def send_message(self, message, telegram_username):
        """
        Send a message to a Telegram user
        
        Args:
            message (str): Message to send
            telegram_username (str): Recipient's Telegram username
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Get the Telegram bot token from settings
            bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
            
            if not bot_token:
                logger.error("Telegram bot token not configured in settings")
                return False, "Telegram bot token not configured"
            
            # Format the username (ensure it starts with @)
            if not telegram_username.startswith('@'):
                telegram_username = f"@{telegram_username}"
            
            # Telegram API URL for sending messages
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # Prepare the payload
            payload = {
                'chat_id': telegram_username,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            # Send the request
            response = requests.post(url, data=payload)
            
            # Check if the request was successful
            if response.status_code == 200 and response.json().get('ok'):
                logger.info(f"Telegram message sent successfully to {telegram_username}")
                return True, None
            else:
                error_msg = response.json().get('description', 'Unknown error')
                logger.error(f"Failed to send Telegram message: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False, str(e)
