from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
import asyncio
import logging

from .models import Email, TelegramSession, TelegramChat, TelegramMessage, TelegramContact
from .forms import EmailForm, EmailSettingsForm
from .telegram_client import TelegramClientManager

class TelebirdIntroView(View):
    def get(self, request):
        return render(request, 'communication/email/telebird_intro.html')

class TelebirdEmailInboxView(LoginRequiredMixin, View):
    def get(self, request):
        # Get inbox emails for the current user
        emails = Email.objects.filter(
            recipients=request.user, 
            is_deleted=False
        ).order_by('-sent_at')
        
        # Get the unread count
        unread_count = emails.filter(is_read=False).count()
        
        # Get the first email to display if available
        current_email = None
        if emails.exists():
            current_email = emails.first()
            # Mark as read
            if not current_email.is_read:
                current_email.is_read = True
                current_email.save()
        
        context = {
            'active_tab': 'inbox',
            'emails': emails,
            'current_email': current_email,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/inbox_telebird.html', context)

class TelebirdEmailSentView(LoginRequiredMixin, View):
    def get(self, request):
        # Get sent emails for the current user
        emails = Email.objects.filter(
            sender=request.user, 
            is_deleted=False, 
            is_draft=False
        ).order_by('-sent_at')
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients=request.user)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        # Get the first email to display if available
        current_email = None
        if emails.exists():
            current_email = emails.first()
        
        context = {
            'active_tab': 'sent',
            'emails': emails,
            'current_email': current_email,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/sent_telebird.html', context)

class TelebirdEmailDraftsView(LoginRequiredMixin, View):
    def get(self, request):
        # Get draft emails for the current user
        emails = Email.objects.filter(
            sender=request.user, 
            is_draft=True, 
            is_deleted=False
        ).order_by('-updated_at')
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients=request.user)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        # Get the first email to display if available
        current_email = None
        if emails.exists():
            current_email = emails.first()
        
        context = {
            'active_tab': 'drafts',
            'emails': emails,
            'current_email': current_email,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/inbox_telebird.html', context)

class TelebirdEmailViewView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # Get the email to view
        email = get_object_or_404(Email, pk=pk)
        
        # Mark as read if it's a received email
        if not email.is_read and request.user in email.recipients.all():
            email.is_read = True
            email.save()
        
        # Get all emails based on the current tab
        if email.sender == request.user and email.is_draft:
            active_tab = 'drafts'
            emails = Email.objects.filter(
                sender=request.user, 
                is_draft=True, 
                is_deleted=False
            ).order_by('-updated_at')
        elif email.sender == request.user:
            active_tab = 'sent'
            emails = Email.objects.filter(
                sender=request.user, 
                is_deleted=False, 
                is_draft=False
            ).order_by('-sent_at')
        else:
            active_tab = 'inbox'
            emails = Email.objects.filter(
                recipients=request.user, 
                is_deleted=False
            ).order_by('-sent_at')
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients=request.user)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        context = {
            'active_tab': active_tab,
            'emails': emails,
            'current_email': email,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/view_telebird.html', context)

class TelebirdEmailComposeView(LoginRequiredMixin, View):
    def get(self, request):
        # Initialize form
        form = EmailForm()
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients=request.user)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        context = {
            'active_tab': 'compose',
            'form': form,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/compose_telebird.html', context)
    
    def post(self, request):
        form = EmailForm(request.POST)
        
        if form.is_valid():
            email = form.save(commit=False)
            email.sender_email = request.user.email
            email.sender_name = request.user.get_full_name() or request.user.username
            
            # Check if saving as draft or sending
            if 'save_draft' in request.POST:
                email.is_draft = True
                email.save()
                
                # Save recipients directly to the many-to-many field
                email.recipients.set(form.cleaned_data['recipients'])
                
                messages.success(request, 'Email saved as draft.')
                return redirect('communication:email_drafts_telebird')
            else:
                # Sending the email
                email.is_draft = False
                email.save()
                
                # Save recipients directly to the many-to-many field
                email.recipients.set(form.cleaned_data['recipients'])
                
                # Here you would actually send the email using your email backend
                
                messages.success(request, 'Email sent successfully.')
                return redirect('communication:email_sent_telebird')
        
        # Form is invalid
        context = {
            'active_tab': 'compose',
            'form': form,
            'unread_count': Email.objects.filter(recipients=request.user, is_read=False).count()
        }
        
        return render(request, 'communication/email/compose_telebird.html', context)

class TelebirdEmailDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        email = get_object_or_404(Email, pk=pk)
        
        # Simple soft delete by marking as deleted
        email.is_deleted = True
        email.save()
        
        messages.success(request, 'Email moved to trash.')
        
        # Redirect based on the source
        redirect_to = request.POST.get('redirect_to', 'inbox')
        if redirect_to == 'sent':
            return redirect('communication:email_sent_telebird')
        elif redirect_to == 'drafts':
            return redirect('communication:email_drafts_telebird')
        else:
            return redirect('communication:email_inbox_telebird')

class TelebirdTelegramClientView(LoginRequiredMixin, View):
    def get(self, request):
        # Get user's Telegram session
        telegram_session = getattr(request.user, 'telegram_session', None)
        
        # Get Telegram chats and messages
        chats = []
        messages = []
        active_chat = None
        
        if telegram_session and telegram_session.is_authenticated:
            # Get user's chats
            chats = TelegramChat.objects.filter(
                user=request.user,
                is_archived=False
            ).order_by('-last_message_date')[:20]
            
            # Get active chat
            chat_id = request.GET.get('chat_id')
            if chat_id:
                try:
                    active_chat = TelegramChat.objects.get(
                        id=chat_id,
                        user=request.user
                    )
                    # Get messages for this chat
                    messages = TelegramMessage.objects.filter(
                        chat=active_chat,
                        is_deleted=False
                    ).order_by('sent_at')[:50]
                except TelegramChat.DoesNotExist:
                    pass
            elif chats.exists():
                active_chat = chats.first()
                messages = TelegramMessage.objects.filter(
                    chat=active_chat,
                    is_deleted=False
                ).order_by('sent_at')[:50]
        
        # Get contacts
        contacts = TelegramContact.objects.filter(
            user=request.user
        ).order_by('first_name')[:50]
        
        context = {
            'active_tab': 'telegram',
            'telegram_session': telegram_session,
            'chats': chats,
            'messages': messages,
            'contacts': contacts,
            'active_chat': active_chat,
            'is_authenticated': telegram_session.is_authenticated if telegram_session else False,
        }
        
        return render(request, 'communication/telegram/telegram_client.html', context)
    
    def post(self, request):
        """Handle AJAX requests for sync and other operations"""
        action = request.POST.get('action')
        
        if action == 'sync_contacts':
            return self._sync_contacts(request)
        elif action == 'sync_chats':
            return self._sync_chats(request)
        elif action == 'sync_messages':
            return self._sync_messages(request)
        elif action == 'test_connection':
            return self._test_connection(request)
        elif action == 'create_chat':
            return self._create_chat(request)
        
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    def _sync_contacts(self, request):
        """Sync Telegram contacts"""
        try:
            session = getattr(request.user, 'telegram_session', None)
            if not session or not session.is_authenticated:
                return JsonResponse({
                    'error': 'Telegram not connected. Please authenticate first.'
                }, status=400)
            
            # Use the management command functionality
            from .management.commands.telegram_client import Command as TelegramCommand
            command = TelegramCommand()
            
            # Create fake options for the command
            options = {
                'user': request.user.username,
                'limit': 100
            }
            
            try:
                command.sync_contacts(options)
                contact_count = TelegramContact.objects.filter(user=request.user).count()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully synced contacts',
                    'count': contact_count
                })
            except Exception as e:
                logging.error(f"Sync contacts error: {e}")
                return JsonResponse({
                    'error': f'Sync failed: {str(e)}'
                }, status=500)
                
        except Exception as e:
            logging.error(f"Sync contacts error: {e}")
            return JsonResponse({
                'error': 'Failed to sync contacts'
            }, status=500)
    
    def _sync_chats(self, request):
        """Sync Telegram chats"""
        try:
            session = getattr(request.user, 'telegram_session', None)
            if not session or not session.is_authenticated:
                return JsonResponse({
                    'error': 'Telegram not connected. Please authenticate first.'
                }, status=400)
                
            from .management.commands.telegram_client import Command as TelegramCommand
            command = TelegramCommand()
            
            options = {
                'user': request.user.username,
                'limit': 50
            }
            
            try:
                command.sync_chats(options)
                chat_count = TelegramChat.objects.filter(user=request.user).count()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully synced chats',
                    'count': chat_count
                })
            except Exception as e:
                logging.error(f"Sync chats error: {e}")
                return JsonResponse({
                    'error': f'Sync failed: {str(e)}'
                }, status=500)
                
        except Exception as e:
            logging.error(f"Sync chats error: {e}")
            return JsonResponse({
                'error': 'Failed to sync chats'
            }, status=500)
    
    def _sync_messages(self, request):
        """Sync recent Telegram messages"""
        try:
            session = getattr(request.user, 'telegram_session', None)
            if not session or not session.is_authenticated:
                return JsonResponse({
                    'error': 'Telegram not connected. Please authenticate first.'
                }, status=400)
                
            from .management.commands.telegram_client import Command as TelegramCommand
            command = TelegramCommand()
            
            options = {
                'user': request.user.username,
                'limit': 100
            }
            
            try:
                command.sync_messages(options)
                message_count = TelegramMessage.objects.filter(user=request.user).count()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully synced messages',
                    'count': message_count
                })
            except Exception as e:
                logging.error(f"Sync messages error: {e}")
                return JsonResponse({
                    'error': f'Sync failed: {str(e)}'
                }, status=500)
                
        except Exception as e:
            logging.error(f"Sync messages error: {e}")
            return JsonResponse({
                'error': 'Failed to sync messages'
            }, status=500)
    
    def _test_connection(self, request):
        """Test Telegram connection"""
        try:
            session = getattr(request.user, 'telegram_session', None)
            if not session:
                return JsonResponse({
                    'error': 'No Telegram session found. Please set up your Telegram credentials first.'
                }, status=400)
                
            if not session.is_authenticated:
                return JsonResponse({
                    'error': 'Telegram session not authenticated. Please authenticate first.'
                }, status=400)
                
            from .management.commands.telegram_client import Command as TelegramCommand
            command = TelegramCommand()
            
            options = {
                'user': request.user.username
            }
            
            try:
                command.test_connection(options)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Telegram connection successful'
                })
            except Exception as e:
                logging.error(f"Test connection error: {e}")
                return JsonResponse({
                    'error': f'Connection test failed: {str(e)}'
                }, status=500)
                
        except Exception as e:
            logging.error(f"Test connection error: {e}")
            return JsonResponse({
                'error': 'Connection test failed'
            }, status=500)
    
    def _create_chat(self, request):
        """Create a new chat with a contact"""
        try:
            contact_id = request.POST.get('contact_id')
            if not contact_id:
                return JsonResponse({
                    'error': 'Contact ID is required'
                }, status=400)
            
            # Find the contact
            try:
                contact = TelegramContact.objects.get(
                    user=request.user,
                    telegram_id=contact_id
                )
            except TelegramContact.DoesNotExist:
                return JsonResponse({
                    'error': 'Contact not found'
                }, status=404)
            
            # Check if chat already exists
            existing_chat = TelegramChat.objects.filter(
                user=request.user,
                contact=contact,
                chat_type='private'
            ).first()
            
            if existing_chat:
                return JsonResponse({
                    'success': True,
                    'chat_id': existing_chat.id,
                    'message': 'Chat already exists'
                })
            
            # Create new chat
            chat = TelegramChat.objects.create(
                user=request.user,
                contact=contact,
                telegram_chat_id=contact.telegram_id,  # For private chats, use contact's telegram_id
                title=f"{contact.first_name} {contact.last_name or ''}".strip(),
                chat_type='private'
            )
            
            return JsonResponse({
                'success': True,
                'chat_id': chat.id,
                'message': 'Chat created successfully'
            })
            
        except Exception as e:
            logging.error(f"Create chat error: {e}")
            return JsonResponse({
                'error': f'Failed to create chat: {str(e)}'
            }, status=500)

class EmailSettingsView(LoginRequiredMixin, View):
    def get(self, request):
        # Initial email settings form
        initial_data = {
            'display_name': request.user.profile.display_name,
            'signature': request.user.profile.email_signature,
            'theme': request.user.profile.email_theme,
            'language': request.user.profile.language,
        }
        form = EmailSettingsForm(initial=initial_data)
        
        context = {
            'form': form,
            'active_tab': 'settings',
        }
        
        return render(request, 'communication/email/email_settings.html', context)
    
    def post(self, request):
        form = EmailSettingsForm(request.POST)
        
        if form.is_valid():
            # Update user profile with email settings
            profile = request.user.profile
            profile.display_name = form.cleaned_data['display_name']
            profile.email_signature = form.cleaned_data['signature']
            profile.email_theme = form.cleaned_data['theme']
            profile.language = form.cleaned_data['language']
            profile.save()
            
            # AJAX response for dynamic update
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Email settings updated successfully.',
                })
            
            # Traditional form submission
            messages.success(request, 'Email settings updated successfully.')
            return redirect('communication:email_settings')
        
        # If form is invalid
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors,
            }, status=400)
        
        # Traditional form submission
        context = {
            'form': form,
            'active_tab': 'settings',
        }
        return render(request, 'communication/email/email_settings.html', context)
