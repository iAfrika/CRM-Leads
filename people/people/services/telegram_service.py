import logging
import telegram
from django.conf import settings
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.bot = telegram.Bot(token=self.bot_token)
    
    def send_message(self, telegram_username, message):
        """send message to a user via Telegram"""
        try:
            # Remove @ symbpl if present
            username = telegram_username.replace('@', '') if telegram_username.startswith('@') else telegram_username

            #Send message
            


         # Send message
            async def send_async_message():
                await self.bot.send_message(chat_id=f"@{username}", text=message)
            
            async_to_sync(send_async_message)()
            return True, "Message sent successfully"
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False, str(e)