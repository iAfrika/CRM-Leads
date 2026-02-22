"""
Django management command for Telegram client operations.

This command provides utilities for:
- Testing Telegram connection
- Syncing contacts and messages
- Managing bot configurations
- Debugging Telegram integration issues
"""

import asyncio
import logging
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

from communication.models import TelegramSession, TelegramContact, TelegramChat, TelegramMessage
from communication.telegram_client import TelegramClientManager

User = get_user_model()

class Command(BaseCommand):
    help = 'Manage Telegram client operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=[
                'test_connection',
                'sync_contacts',
                'sync_chats',
                'sync_messages',
                'create_session',
                'authenticate_session',
                'list_sessions',
                'delete_session',
                'send_test_message',
                'export_data'
            ],
            help='Action to perform'
        )
        
        parser.add_argument(
            '--user',
            type=str,
            help='Username or user ID to perform action for'
        )
        
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number for Telegram authentication'
        )
        
        parser.add_argument(
            '--api-id',
            type=str,
            help='Telegram API ID'
        )
        
        parser.add_argument(
            '--api-hash',
            type=str,
            help='Telegram API Hash'
        )
        
        parser.add_argument(
            '--chat-id',
            type=str,
            help='Telegram chat ID for specific operations'
        )
        
        parser.add_argument(
            '--message',
            type=str,
            help='Message text to send'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output file for export operations'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Limit for sync operations'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        try:
            if action == 'test_connection':
                self.test_connection(options)
            elif action == 'sync_contacts':
                self.sync_contacts(options)
            elif action == 'sync_chats':
                self.sync_chats(options)
            elif action == 'sync_messages':
                self.sync_messages(options)
            elif action == 'create_session':
                self.create_session(options)
            elif action == 'authenticate_session':
                self.authenticate_session(options)
            elif action == 'list_sessions':
                self.list_sessions()
            elif action == 'delete_session':
                self.delete_session(options)
            elif action == 'send_test_message':
                self.send_test_message(options)
            elif action == 'export_data':
                self.export_data(options)
        except Exception as e:
            raise CommandError(f'Error executing {action}: {e}')

    def get_user(self, options):
        """Get user from options or prompt for selection."""
        user_identifier = options.get('user')
        
        if user_identifier:
            try:
                if user_identifier.isdigit():
                    return User.objects.get(id=int(user_identifier))
                else:
                    return User.objects.get(username=user_identifier)
            except User.DoesNotExist:
                raise CommandError(f'User not found: {user_identifier}')
        
        # List available users
        users = User.objects.all()
        if not users.exists():
            raise CommandError('No users found in the system')
        
        self.stdout.write('Available users:')
        for i, user in enumerate(users, 1):
            self.stdout.write(f'{i}. {user.username} (ID: {user.id})')
        
        try:
            choice = input('Select user (number): ')
            return users[int(choice) - 1]
        except (ValueError, IndexError):
            raise CommandError('Invalid user selection')

    def test_connection(self, options):
        """Test Telegram connection for a user."""
        user = self.get_user(options)
        
        self.stdout.write(f'Testing Telegram connection for user: {user.username}')
        
        try:
            session = TelegramSession.objects.get(user=user)
        except TelegramSession.DoesNotExist:
            raise CommandError('No Telegram session found for this user. Create one first.')
        
        if not session.is_authenticated:
            raise CommandError('User not authenticated with Telegram')
        
        # Test connection
        client = TelegramClientManager(
            user=user,
            api_id=session.api_id,
            api_hash=session.api_hash
        )
        
        async def test():
            success = await client.initialize_user_client()
            if success:
                me = await client.client.get_me()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Connected successfully as {me.first_name} {me.last_name or ""} '
                        f'(@{me.username or "no_username"})'
                    )
                )
                await client.stop_client()
                return True
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to connect'))
                return False
        
        result = asyncio.run(test())
        
        if result:
            session.last_activity = timezone.now()
            session.save()

    def sync_contacts(self, options):
        """Sync Telegram contacts for a user."""
        user = self.get_user(options)
        limit = options.get('limit', 100)
        
        self.stdout.write(f'Syncing contacts for user: {user.username}')
        
        # Get session data
        try:
            session = TelegramSession.objects.get(user=user)
        except TelegramSession.DoesNotExist:
            raise CommandError('No Telegram session found for this user. Create one first.')
        
        if not session.is_authenticated:
            raise CommandError('User not authenticated with Telegram')
        
        client = TelegramClientManager(
            user=user,
            api_id=session.api_id,
            api_hash=session.api_hash
        )
        
        def run_sync():
            import asyncio
            
            async def fetch_contacts():
                """Fetch contacts from Telegram without database operations."""
                try:
                    await client.initialize_user_client()
                    contacts = await client.get_contacts()
                    await client.stop_client()
                    return contacts[:limit]
                except Exception as e:
                    raise e
            
            # Use a new event loop in the thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(fetch_contacts())
            finally:
                loop.close()
        
        try:
            # Run Telegram operations in a thread to avoid async context issues
            import threading
            contacts_data = None
            exception = None
            
            def sync_thread():
                nonlocal contacts_data, exception
                try:
                    contacts_data = run_sync()
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=sync_thread)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
                
            # Process contacts synchronously (no async context issues)
            synced_count = 0
            updated_count = 0
            
            for contact_data in contacts_data:
                contact, created = TelegramContact.objects.get_or_create(
                    user=user,
                    telegram_id=contact_data['id'],
                    defaults={
                        'first_name': contact_data['first_name'],
                        'last_name': contact_data['last_name'],
                        'username': contact_data['username'],
                        'phone_number': contact_data['phone_number'],
                        'is_verified': contact_data.get('is_verified', False),
                        'is_premium': contact_data.get('is_premium', False),
                        'is_contact': contact_data.get('is_contact', False),
                        'is_mutual_contact': contact_data.get('is_mutual_contact', False),
                    }
                )
                
                if created:
                    synced_count += 1
                else:
                    # Update existing contact
                    contact.first_name = contact_data['first_name']
                    contact.last_name = contact_data['last_name']
                    contact.username = contact_data['username']
                    contact.phone_number = contact_data['phone_number']
                    contact.is_verified = contact_data.get('is_verified', False)
                    contact.is_premium = contact_data.get('is_premium', False)
                    contact.save()
                    updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Synced {synced_count} new contacts, updated {updated_count} existing'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to sync contacts: {e}'))

    def sync_chats(self, options):
        """Sync Telegram chats for a user."""
        user = self.get_user(options)
        limit = options.get('limit', 50)
        
        self.stdout.write(f'Syncing chats for user: {user.username}')
        
        # Get session data
        try:
            session = TelegramSession.objects.get(user=user)
        except TelegramSession.DoesNotExist:
            raise CommandError('No Telegram session found for this user. Create one first.')
        
        if not session.is_authenticated:
            raise CommandError('User not authenticated with Telegram')
        
        client = TelegramClientManager(
            user=user,
            api_id=session.api_id,
            api_hash=session.api_hash
        )
        
        def run_sync():
            import asyncio
            
            async def fetch_chats():
                """Fetch chats from Telegram without database operations."""
                try:
                    await client.initialize_user_client()
                    chats = await client.get_chats()
                    await client.stop_client()
                    return chats[:limit]
                except Exception as e:
                    raise e
            
            # Use a new event loop in the thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(fetch_chats())
            finally:
                loop.close()
        
        try:
            # Run Telegram operations in a thread to avoid async context issues
            import threading
            chats_data = None
            exception = None
            
            def sync_thread():
                nonlocal chats_data, exception
                try:
                    chats_data = run_sync()
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=sync_thread)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
                
            # Process chats synchronously (no async context issues)
            synced_count = 0
            
            for chat_data in chats_data:
                # Get or create contact if it's a private chat
                contact = None
                if chat_data['type'] == 'private':
                    try:
                        contact = TelegramContact.objects.get(
                            user=user,
                            telegram_id=chat_data['id']
                        )
                    except TelegramContact.DoesNotExist:
                        pass
                
                chat, created = TelegramChat.objects.get_or_create(
                    user=user,
                    telegram_chat_id=chat_data['id'],
                    defaults={
                        'chat_type': chat_data['type'],
                        'title': chat_data['title'],
                        'contact': contact,
                        'last_message_date': chat_data.get('last_message_date'),
                        'unread_count': chat_data.get('unread_count', 0),
                    }
                )
                
                if created:
                    synced_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Synced {synced_count} new chats')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to sync chats: {e}'))

    def sync_messages(self, options):
        """Sync recent messages for a user."""
        user = self.get_user(options)
        chat_id = options.get('chat_id')
        limit = options.get('limit', 100)
        
        self.stdout.write(f'Syncing messages for user: {user.username}')
        
        # Get session data
        try:
            session = TelegramSession.objects.get(user=user)
        except TelegramSession.DoesNotExist:
            raise CommandError('No Telegram session found for this user. Create one first.')
        
        if not session.is_authenticated:
            raise CommandError('User not authenticated with Telegram')
        
        client = TelegramClientManager(
            user=user,
            api_id=session.api_id,
            api_hash=session.api_hash
        )
        
        def run_sync():
            import asyncio
            
            async def fetch_messages():
                """Fetch messages from Telegram without database operations."""
                try:
                    await client.initialize_user_client()
                    
                    if chat_id:
                        # Sync specific chat
                        chats = [{'id': int(chat_id)}]
                    else:
                        # Sync all chats
                        chats = await client.get_chats()
                    
                    all_messages = []
                    
                    for chat_data in chats[:10]:  # Limit to 10 chats to avoid overwhelming
                        try:
                            messages = await client.get_chat_messages(chat_data['id'], limit=limit)
                            for msg_data in messages:
                                msg_data['chat_id'] = chat_data['id']
                            all_messages.extend(messages)
                        except Exception as e:
                            self.stdout.write(f'Warning: Could not fetch messages for chat {chat_data["id"]}: {e}')
                            continue
                    
                    await client.stop_client()
                    return all_messages
                except Exception as e:
                    raise e
            
            # Use a new event loop in the thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(fetch_messages())
            finally:
                loop.close()
        
        try:
            # Run Telegram operations in a thread to avoid async context issues
            import threading
            messages_data = None
            exception = None
            
            def sync_thread():
                nonlocal messages_data, exception
                try:
                    messages_data = run_sync()
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=sync_thread)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
                
            # Process messages synchronously (no async context issues)
            total_synced = 0
            
            for msg_data in messages_data:
                try:
                    # Find the chat
                    chat = TelegramChat.objects.get(
                        user=user,
                        telegram_chat_id=msg_data['chat_id']
                    )
                except TelegramChat.DoesNotExist:
                    continue
                
                # Check if message already exists
                message_id = msg_data.get('id')
                if message_id and not TelegramMessage.objects.filter(
                    user=user,
                    telegram_message_id=message_id,
                    telegram_chat_id=msg_data['chat_id']
                ).exists():
                    
                    # Get contact for the message sender
                    contact = None
                    if msg_data.get('from_user'):
                        try:
                            contact = TelegramContact.objects.get(
                                user=user,
                                telegram_id=msg_data['from_user']['id']
                            )
                        except TelegramContact.DoesNotExist:
                            pass
                    
                    TelegramMessage.objects.create(
                        user=user,
                        chat=chat,
                        contact=contact,
                        telegram_message_id=msg_data.get('id'),
                        telegram_chat_id=msg_data['chat_id'],
                        message_text=msg_data.get('text', ''),
                        is_outgoing=bool(msg_data.get('is_outgoing', False)),
                        sent_at=msg_data.get('date'),
                        status='read' if not bool(msg_data.get('is_outgoing', False)) else 'sent',
                        message_type='text'
                    )
                    total_synced += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Synced {total_synced} total messages')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to sync messages: {e}'))

    def create_session(self, options):
        """Create a new Telegram session for a user."""
        user = self.get_user(options)
        phone = options.get('phone')
        api_id = options.get('api_id')
        api_hash = options.get('api_hash')
        
        if not phone:
            phone = input('Enter phone number (with country code): ')
        
        if not api_id:
            api_id = input('Enter Telegram API ID: ')
        
        if not api_hash:
            api_hash = input('Enter Telegram API Hash: ')
        
        session, created = TelegramSession.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': phone,
                'api_id': api_id,
                'api_hash': api_hash,
                'is_authenticated': False,
            }
        )
        
        if not created:
            session.phone_number = phone
            session.api_id = api_id
            session.api_hash = api_hash
            session.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ {"Created" if created else "Updated"} Telegram session for {user.username}'
            )
        )

    def authenticate_session(self, options):
        """Authenticate a Telegram session with phone verification."""
        user = self.get_user(options)
        
        try:
            session = TelegramSession.objects.get(user=user)
        except TelegramSession.DoesNotExist:
            raise CommandError('No Telegram session found for this user. Create one first.')
        
        if session.is_authenticated:
            self.stdout.write(
                self.style.SUCCESS(f'✓ User {user.username} is already authenticated')
            )
            return
        
        self.stdout.write(f'Authenticating Telegram session for user: {user.username}')
        self.stdout.write(f'Phone: {session.phone_number}')
        
        # Import Pyrogram for authentication
        try:
            from pyrogram import Client
            from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired
        except ImportError:
            raise CommandError('Pyrogram is required for authentication')
        
        # Create a temporary client for authentication
        session_name = f"auth_session_{user.id}"
        client = Client(
            session_name,
            api_id=int(session.api_id),
            api_hash=session.api_hash,
            phone_number=session.phone_number
        )
        
        async def authenticate():
            try:
                await client.connect()
                
                # Check if already authorized
                try:
                    me = await client.get_me()
                    self.stdout.write(
                        self.style.SUCCESS('✓ Already authenticated!')
                    )
                    session.is_authenticated = True
                    session.save()
                    return True
                except Exception:
                    # Not authenticated, need to send code
                    pass
                
                # Send verification code
                self.stdout.write('📱 Sending verification code to your phone...')
                sent_code = await client.send_code(session.phone_number)
                
                # Prompt for verification code
                code = input('Enter the verification code you received: ').strip()
                
                # Verify the code
                await client.sign_in(session.phone_number, sent_code.phone_code_hash, code)
                
                # Get user info
                me = await client.get_me()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Successfully authenticated as {me.first_name} {me.last_name or ""}'
                    )
                )
                
                # Update session status
                session.is_authenticated = True
                session.last_activity = timezone.now()
                session.save()
                
                return True
                
            except SessionPasswordNeeded:
                # 2FA is enabled
                password = input('Enter your 2FA password: ').strip()
                await client.check_password(password)
                
                me = await client.get_me()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Successfully authenticated with 2FA as {me.first_name} {me.last_name or ""}'
                    )
                )
                
                session.is_authenticated = True
                session.last_activity = timezone.now()
                session.save()
                
                return True
                
            except PhoneCodeInvalid:
                self.stdout.write(self.style.ERROR('✗ Invalid verification code'))
                return False
                
            except PhoneCodeExpired:
                self.stdout.write(self.style.ERROR('✗ Verification code expired'))
                return False
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Authentication failed: {e}'))
                return False
                
            finally:
                try:
                    await client.disconnect()
                except:
                    pass
        
        # Run the authentication using a different approach
        import threading
        result = {'success': False, 'error': None}
        
        def run_auth():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result['success'] = loop.run_until_complete(authenticate())
            except Exception as e:
                result['error'] = str(e)
            finally:
                loop.close()
        
        auth_thread = threading.Thread(target=run_auth)
        auth_thread.start()
        auth_thread.join()
        
        # Check the result
        if result.get('success'):
            # Force update the session status
            session.refresh_from_db()
            session.is_authenticated = True
            session.last_activity = timezone.now()
            session.save()
            result_success = True
        else:
            result_success = False
        
        if result_success:
            self.stdout.write(
                self.style.SUCCESS('🎉 Telegram authentication completed successfully!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Telegram authentication failed')
            )

    def list_sessions(self):
        """List all Telegram sessions."""
        sessions = TelegramSession.objects.all()
        
        if not sessions.exists():
            self.stdout.write(self.style.WARNING('No Telegram sessions found'))
            return
        
        self.stdout.write('Telegram Sessions:')
        self.stdout.write('-' * 80)
        
        for session in sessions:
            status = '✓ Authenticated' if session.is_authenticated else '✗ Not authenticated'
            self.stdout.write(
                f'{session.user.username:20} {session.phone_number:15} {status:20} '
                f'Last: {session.last_activity.strftime("%Y-%m-%d %H:%M") if session.last_activity else "Never"}'
            )

    def delete_session(self, options):
        """Delete a Telegram session."""
        user = self.get_user(options)
        
        try:
            session = TelegramSession.objects.get(user=user)
            session.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Deleted Telegram session for {user.username}')
            )
        except TelegramSession.DoesNotExist:
            raise CommandError(f'No Telegram session found for user: {user.username}')

    def send_test_message(self, options):
        """Send a test message via Telegram."""
        user = self.get_user(options)
        chat_id = options.get('chat_id')
        message = options.get('message', 'Test message from CRM Leads Telegram client')
        
        if not chat_id:
            chat_id = input('Enter chat ID to send message to: ')
        
        client = TelegramClientManager(user=user)
        
        async def send():
            await client.initialize_user_client()
            result = await client.send_message(int(chat_id), message)
            await client.stop_client()
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Message sent successfully: {result}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to send message: {result["error"]}')
                )
        
        asyncio.run(send())

    def export_data(self, options):
        """Export Telegram data for a user."""
        user = self.get_user(options)
        output_file = options.get('output', f'telegram_export_{user.username}.json')
        
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        
        # Collect data
        contacts = list(TelegramContact.objects.filter(user=user).values())
        chats = list(TelegramChat.objects.filter(user=user).values())
        messages = list(TelegramMessage.objects.filter(user=user).values())
        
        export_data = {
            'user': user.username,
            'export_date': timezone.now().isoformat(),
            'contacts': contacts,
            'chats': chats,
            'messages': messages,
            'statistics': {
                'total_contacts': len(contacts),
                'total_chats': len(chats),
                'total_messages': len(messages),
            }
        }
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, cls=DjangoJSONEncoder, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Data exported to {output_file}')
        )
