# Telegram Client Integration for CRM-Leads

This document describes the comprehensive Telegram client integration that has been added to the CRM-Leads communication app. The integration provides real-time messaging capabilities similar to the official Telegram client.

## Features

### 🚀 Core Features
- **Real-time messaging** with live chat interface
- **Contact management** with Telegram-specific data
- **Media sharing** (photos, videos, documents, audio)
- **Message synchronization** with Telegram servers
- **Bot integration** for automated messaging
- **Search functionality** across messages and contacts
- **Export capabilities** for data backup
- **Webhook support** for real-time updates

### 💬 Messaging Features
- Send and receive text messages
- Share media files with captions
- Reply to messages
- Message status tracking (sent, delivered, read)
- Typing indicators
- Message search within chats
- Message history with pagination

### 👥 Contact Management
- Import contacts from Telegram
- Sync contact information automatically
- Display verification status, premium status
- Contact search and filtering
- Profile photos and bio information

### 🔧 Admin Features
- Django admin integration
- Management commands for bulk operations
- User session management
- Bot configuration and management
- Webhook configuration for real-time updates

## Installation & Setup

### 1. Install Dependencies

The required packages are already listed in `requirements.txt`:

```pip-requirements
python-telegram-bot==20.7
pyrogram==2.0.106
```

Install them:

```bash
pip install python-telegram-bot pyrogram
```

### 2. Get Telegram API Credentials

1. Go to [https://my.telegram.org/apps](https://my.telegram.org/apps)
2. Log in with your Telegram account
3. Create a new application
4. Note down the `API ID` and `API Hash`

### 3. Django Settings

Add to your `settings.py`:

```python
# Telegram Configuration
TELEGRAM_API_ID = 'your_api_id'
TELEGRAM_API_HASH = 'your_api_hash'
TELEGRAM_BOT_TOKEN = 'your_bot_token'  # Optional, for bot features

# Media storage for Telegram files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

### 4. Database Migration

Run migrations to create the new Telegram models:

```bash
python manage.py makemigrations communication
python manage.py migrate
```

### 5. Setup User Session

Use the management command to create a Telegram session for a user:

```bash
python manage.py telegram_client create_session --user username --phone +1234567890 --api-id YOUR_API_ID --api-hash YOUR_API_HASH
```

## Usage

### Web Interface

1. **Access Telegram Client**: Navigate to `/communication/telegram/`
2. **Settings**: Configure API credentials at `/communication/telegram/settings/`
3. **Contacts**: Manage contacts at `/communication/telegram/contacts/`

### Management Commands

The integration includes comprehensive management commands:

```bash
# Test connection
python manage.py telegram_client test_connection --user username

# Sync contacts
python manage.py telegram_client sync_contacts --user username --limit 100

# Sync chats
python manage.py telegram_client sync_chats --user username

# Sync messages
python manage.py telegram_client sync_messages --user username --limit 50

# List all sessions
python manage.py telegram_client list_sessions

# Send test message
python manage.py telegram_client send_test_message --user username --chat-id 123456 --message "Hello!"

# Export data
python manage.py telegram_client export_data --user username --output telegram_backup.json
```

## Models

### TelegramContact
Stores Telegram contact information with verification status, premium status, and profile data.

### TelegramChat
Represents chats (private, groups, channels) with metadata like unread counts and settings.

### TelegramMessage
Stores individual messages with media support, delivery status, and relationship to chats.

### TelegramSession
Manages user authentication sessions with Telegram servers.

### TelegramBot
Configuration for Telegram bots with webhook settings.

## API Integration

### Real-time Features

The integration supports:
- **WebSocket connections** for real-time updates
- **Webhook handlers** for incoming messages
- **Background synchronization** using Celery (if configured)

### Message Sending

```python
from communication.telegram_client import get_telegram_client

client = get_telegram_client(user)
await client.initialize_user_client()

# Send text message
result = await client.send_message(chat_id, "Hello, World!")

# Send media
result = await client.send_media(chat_id, "/path/to/file.jpg", "Caption")
```

### Data Synchronization

```python
from communication.telegram_client import sync_telegram_contacts, sync_telegram_messages

# Sync contacts
synced_count = await sync_telegram_contacts(user)

# Sync messages for specific chat
synced_count = await sync_telegram_messages(user, chat_id=123456)
```

## Security & Privacy

### Data Protection
- API credentials are stored encrypted
- Session data is securely managed
- Media files are stored with proper access controls
- User data synchronization respects privacy settings

### Authentication
- Uses official Telegram authentication methods
- Session management with automatic renewal
- Secure token storage and handling

## File Structure

```
communication/
├── telegram_client.py          # Core Telegram client integration
├── views_telegram.py           # Telegram-specific views
├── models.py                   # Enhanced with Telegram models
├── forms.py                    # Telegram forms
├── urls.py                     # Updated with Telegram URLs
├── management/
│   └── commands/
│       └── telegram_client.py  # Management command
└── templates/
    └── communication/
        └── telegram/
            ├── main.html        # Main chat interface
            ├── settings.html    # Settings page
            └── contacts.html    # Contacts management
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify API credentials
   - Check phone number format (+country code)
   - Ensure network connectivity

2. **Authentication Issues**
   - Delete and recreate session
   - Verify phone number is registered with Telegram
   - Check if 2FA is enabled

3. **Sync Problems**
   - Check rate limits (Telegram has API limits)
   - Verify user permissions
   - Review Django logs for errors

4. **Media Upload Issues**
   - Check file size limits
   - Verify MEDIA_ROOT settings
   - Ensure proper file permissions

### Debug Commands

```bash
# Check connection status
python manage.py telegram_client test_connection --user username

# View all sessions
python manage.py telegram_client list_sessions

# Test with verbose output
python manage.py telegram_client sync_contacts --user username --verbosity 2
```

## Development

### Adding New Features

1. **Custom Message Types**: Extend `TelegramMessage` model
2. **Additional Sync Options**: Modify sync methods in `telegram_client.py`
3. **UI Enhancements**: Update templates and add JavaScript features
4. **Bot Commands**: Extend bot handling in webhook views

### Testing

```bash
# Run tests
python manage.py test communication.tests.test_telegram

# Send test message
python manage.py telegram_client send_test_message --user testuser --chat-id 123
```

## Performance Considerations

### Optimization Tips
- Use pagination for message lists
- Implement background sync with Celery
- Cache frequently accessed data
- Optimize database queries with select_related/prefetch_related

### Rate Limiting
- Telegram API has rate limits
- Implement exponential backoff
- Use batch operations where possible
- Monitor API usage

## Contributing

When contributing to the Telegram integration:

1. Follow Django best practices
2. Add tests for new features
3. Update documentation
4. Consider security implications
5. Test with real Telegram data

## License & Legal

- This integration uses the official Telegram APIs
- Respects Telegram's Terms of Service
- User data handling complies with privacy regulations
- Open source under the same license as the main project

## Support

For issues with the Telegram integration:
1. Check this documentation
2. Review Django logs
3. Test with management commands
4. Check Telegram API status

---

*This integration provides a production-ready Telegram client within your CRM system, enabling seamless communication with your contacts through the familiar Telegram interface.*
