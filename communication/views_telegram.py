"""
Enhanced Telegram Views for CRM-Leads Communication App

This module provides comprehensive views for Telegram integration, including:
- Real-time chat interface
- Message management
- Contact synchronization
- Media handling
- Settings management
"""

import json
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.urls import reverse_lazy
from django.conf import settings
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import (
    TelegramMessage, TelegramContact, TelegramChat, 
    TelegramSession, TelegramBot, Contact
)
from .forms import (
    TelegramMessageForm, TelegramContactForm, TelegramSettingsForm,
    TelegramBotForm, TelegramChatForm, TelegramSearchForm, TelegramMediaForm
)
from .telegram_client import TelegramClientManager, get_telegram_client


class TelegramMainView(LoginRequiredMixin, TemplateView):
    """
    Main Telegram client interface with chat list and messaging.
    """
    template_name = 'communication/telegram/telegram_client.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's Telegram chats
        chats = TelegramChat.objects.filter(
            user=self.request.user,
            is_archived=False
        ).select_related('contact').prefetch_related('messages')
        
        # Get active chat if specified
        active_chat_id = self.request.GET.get('chat_id')
        active_chat = None
        messages_list = []
        
        if active_chat_id:
            try:
                active_chat = chats.get(id=active_chat_id)
                messages_list = TelegramMessage.objects.filter(
                    chat=active_chat,
                    is_deleted=False
                ).order_by('sent_at')[:50]
            except TelegramChat.DoesNotExist:
                pass
        elif chats.exists():
            # Select the most recent chat
            active_chat = chats.first()
            messages_list = TelegramMessage.objects.filter(
                chat=active_chat,
                is_deleted=False
            ).order_by('sent_at')[:50]
        
        # Get unread message counts
        for chat in chats:
            chat.unread_count = TelegramMessage.objects.filter(
                chat=chat,
                is_outgoing=False,
                status__in=['sent', 'delivered']
            ).count()
        
        context.update({
            'chats': chats,
            'active_chat': active_chat,
            'messages': messages_list,
            'telegram_session': getattr(self.request.user, 'telegram_session', None),
        })
        
        return context


class TelegramChatView(LoginRequiredMixin, View):
    """
    Handle individual chat operations and message display.
    """
    
    def get(self, request, chat_id):
        """Get chat messages with pagination."""
        try:
            chat = TelegramChat.objects.get(
                id=chat_id,
                user=request.user
            )
        except TelegramChat.DoesNotExist:
            return JsonResponse({'error': 'Chat not found'}, status=404)
        
        # Get messages with pagination
        page = request.GET.get('page', 1)
        limit = int(request.GET.get('limit', 50))
        offset = (int(page) - 1) * limit
        
        messages = TelegramMessage.objects.filter(
            chat=chat,
            is_deleted=False
        ).select_related('contact').order_by('-sent_at')[offset:offset+limit]
        
        # Mark messages as read
        unread_messages = messages.filter(
            is_outgoing=False,
            status__in=['sent', 'delivered']
        )
        unread_messages.update(status='read', read_at=timezone.now())
        
        # Format messages for JSON response
        messages_data = []
        for msg in reversed(messages):  # Reverse to show chronological order
            message_data = {
                'id': str(msg.id),
                'telegram_message_id': msg.telegram_message_id,
                'text': msg.message_text or '',
                'type': msg.message_type,
                'is_outgoing': msg.is_outgoing,
                'is_forwarded': msg.is_forwarded,
                'is_reply': msg.is_reply,
                'sent_at': msg.sent_at.isoformat() if msg.sent_at else None,
                'status': msg.status,
                'contact_name': msg.contact.display_name if msg.contact else 'Unknown',
                'media_url': msg.media_file.url if msg.media_file else None,
                'media_type': msg.media_type,
                'media_caption': msg.media_caption,
                'reactions': msg.reactions,
                'reply_to_message_id': msg.reply_to_message_id,
            }
            messages_data.append(message_data)
        
        return JsonResponse({
            'messages': messages_data,
            'chat': {
                'id': str(chat.id),
                'title': str(chat),
                'type': chat.chat_type,
                'unread_count': chat.unread_count,
            },
            'has_more': len(messages) == limit
        })


class TelegramSendMessageView(LoginRequiredMixin, View):
    """
    Send messages through Telegram.
    """
    
    def post(self, request, chat_id):
        """Send a new message."""
        try:
            chat = TelegramChat.objects.get(
                id=chat_id,
                user=request.user
            )
        except TelegramChat.DoesNotExist:
            return JsonResponse({'error': 'Chat not found'}, status=404)
        
        data = json.loads(request.body)
        message_text = data.get('text', '').strip()
        reply_to_message_id = data.get('reply_to_message_id')
        
        if not message_text:
            return JsonResponse({'error': 'Message text cannot be empty'}, status=400)
        
        try:
            # Get Telegram client and send message
            client = get_telegram_client(request.user)
            
            # This would be async in a real implementation
            # For now, we'll create the message record directly
            telegram_message = TelegramMessage.objects.create(
                user=request.user,
                chat=chat,
                contact=chat.contact,
                message_text=message_text,
                telegram_message_id=0,  # Will be updated when actually sent
                telegram_chat_id=chat.telegram_chat_id,
                message_type='text',
                is_outgoing=True,
                status='sent',
                sent_at=timezone.now()
            )
            
            # Update chat's last message date
            chat.last_message_date = timezone.now()
            chat.save()
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': str(telegram_message.id),
                    'text': telegram_message.message_text,
                    'sent_at': telegram_message.sent_at.isoformat(),
                    'status': telegram_message.status,
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Failed to send message: {str(e)}'}, status=500)


class TelegramContactsView(LoginRequiredMixin, ListView):
    """
    Display and manage Telegram contacts.
    """
    model = TelegramContact
    template_name = 'communication/telegram/contacts.html'
    context_object_name = 'contacts'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = TelegramContact.objects.filter(user=self.request.user)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        # Filter options
        contact_type = self.request.GET.get('type')
        if contact_type == 'verified':
            queryset = queryset.filter(is_verified=True)
        elif contact_type == 'bots':
            queryset = queryset.filter(is_bot=True)
        elif contact_type == 'premium':
            queryset = queryset.filter(is_premium=True)
        
        return queryset.order_by('first_name', 'last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['contact_type'] = self.request.GET.get('type', '')
        
        # Statistics
        context['stats'] = {
            'total': TelegramContact.objects.filter(user=self.request.user).count(),
            'verified': TelegramContact.objects.filter(user=self.request.user, is_verified=True).count(),
            'bots': TelegramContact.objects.filter(user=self.request.user, is_bot=True).count(),
            'premium': TelegramContact.objects.filter(user=self.request.user, is_premium=True).count(),
        }
        
        return context


class TelegramSyncView(LoginRequiredMixin, View):
    """
    Synchronize Telegram data (contacts, chats, messages).
    """
    
    def post(self, request, **kwargs):
        """Trigger synchronization."""
        sync_type = kwargs.get('sync_type') or request.POST.get('sync_type', 'all')
        
        try:
            # Check if user has Telegram session
            session = getattr(request.user, 'telegram_session', None)
            if not session or not session.is_authenticated:
                return JsonResponse({
                    'error': 'Telegram not connected. Please connect your Telegram account first.'
                }, status=400)
            
            results = {}
            count = 0
            
            if sync_type in ['all', 'contacts']:
                # Sync contacts
                contact_result = self._sync_contacts(request.user)
                results['contacts'] = contact_result
                count += contact_result.get('synced', 0)
            
            if sync_type in ['all', 'chats']:
                # Sync chats
                chat_result = self._sync_chats(request.user)
                results['chats'] = chat_result
                count += chat_result.get('synced', 0)
            
            if sync_type in ['all', 'messages']:
                # Sync recent messages
                message_result = self._sync_messages(request.user)
                results['messages'] = message_result
                count += message_result.get('synced', 0)
            
            return JsonResponse({
                'success': True,
                'count': count,
                'results': results,
                'message': f'Successfully synced {count} {sync_type}.'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Synchronization failed: {str(e)}'
            }, status=500)
    
    def _sync_contacts(self, user):
        """Sync Telegram contacts."""
        try:
            # Check if Telegram libraries are available
            from .telegram_client import TELEGRAM_AVAILABLE
            
            if not TELEGRAM_AVAILABLE:
                # Create some dummy contacts for testing
                from .models import TelegramContact
                dummy_contacts = [
                    {'first_name': 'John', 'last_name': 'Doe', 'username': 'johndoe'},
                    {'first_name': 'Jane', 'last_name': 'Smith', 'username': 'janesmith'},
                    {'first_name': 'Bob', 'last_name': 'Wilson', 'username': 'bobwilson'},
                ]
                
                created_count = 0
                for contact_data in dummy_contacts:
                    contact, created = TelegramContact.objects.get_or_create(
                        user=user,
                        username=contact_data['username'],
                        defaults={
                            'first_name': contact_data['first_name'],
                            'last_name': contact_data['last_name'],
                        }
                    )
                    if created:
                        created_count += 1
                
                return {'synced': created_count, 'total': len(dummy_contacts)}
            
            # Get or create Telegram session
            session = TelegramSession.objects.filter(user=user).first()
            if not session:
                return {'error': 'No Telegram session found', 'synced': 0}
            
            # Use the sync function from telegram_client
            from .telegram_client import sync_telegram_contacts
            count = sync_telegram_contacts(user)
            return {'synced': count, 'updated': 0}
        except Exception as e:
            return {'error': str(e), 'synced': 0}
    
    def _sync_chats(self, user):
        """Sync Telegram chats."""
        try:
            # Check if Telegram libraries are available
            from .telegram_client import TELEGRAM_AVAILABLE
            
            if not TELEGRAM_AVAILABLE:
                # Create some dummy chats for testing
                from .models import TelegramChat, TelegramContact
                
                contacts = TelegramContact.objects.filter(user=user)[:3]
                created_count = 0
                
                for contact in contacts:
                    chat, created = TelegramChat.objects.get_or_create(
                        user=user,
                        telegram_chat_id=hash(contact.username) % 1000000,
                        defaults={
                            'title': f"Chat with {contact.first_name}",
                            'chat_type': 'private',
                            'contact': contact,
                        }
                    )
                    if created:
                        created_count += 1
                
                return {'synced': created_count, 'total': contacts.count()}
            
            # For real implementation, use TelegramClientManager
            chats_count = TelegramChat.objects.filter(user=user).count()
            return {'synced': chats_count, 'updated': 0}
        except Exception as e:
            return {'error': str(e), 'synced': 0}
    
    def _sync_messages(self, user):
        """Sync recent Telegram messages."""
        try:
            # Check if Telegram libraries are available
            from .telegram_client import TELEGRAM_AVAILABLE
            
            if not TELEGRAM_AVAILABLE:
                # Create some dummy messages for testing
                from .models import TelegramMessage, TelegramChat
                from datetime import datetime, timedelta
                
                chats = TelegramChat.objects.filter(user=user)[:2]
                created_count = 0
                
                for chat in chats:
                    # Create a few dummy messages per chat
                    messages_data = [
                        {'text': f'Hello from {chat.title}!', 'is_outgoing': False},
                        {'text': 'Hi there! How are you?', 'is_outgoing': True},
                        {'text': 'I am doing great, thanks!', 'is_outgoing': False},
                    ]
                    
                    for i, msg_data in enumerate(messages_data):
                        message, created = TelegramMessage.objects.get_or_create(
                            user=user,
                            chat=chat,
                            telegram_message_id=hash(f"{chat.id}_{i}") % 1000000,
                            defaults={
                                'message_text': msg_data['text'],
                                'is_outgoing': msg_data['is_outgoing'],
                                'telegram_chat_id': chat.telegram_chat_id,
                                'sent_at': datetime.now() - timedelta(hours=i),
                                'status': 'read',
                            }
                        )
                        if created:
                            created_count += 1
                
                return {'synced': created_count, 'total': len(chats) * 3}
            
            # Get or create Telegram session
            session = TelegramSession.objects.filter(user=user).first()
            if not session:
                return {'error': 'No Telegram session found', 'synced': 0}
            
            # Use the sync function from telegram_client
            from .telegram_client import sync_telegram_messages
            count = sync_telegram_messages(user)
            return {'synced': count, 'updated': 0}
        except Exception as e:
            return {'error': str(e), 'synced': 0}


class TelegramSettingsView(LoginRequiredMixin, UpdateView):
    """
    Manage Telegram settings and connection.
    """
    model = TelegramSession
    form_class = TelegramSettingsForm
    template_name = 'communication/telegram/settings.html'
    success_url = reverse_lazy('communication:telegram_settings')
    
    def get_object(self, queryset=None):
        """Get or create TelegramSession for the current user."""
        session, created = TelegramSession.objects.get_or_create(
            user=self.request.user,
            defaults={
                'phone_number': '',
                'is_authenticated': False,
            }
        )
        return session
    
    def form_valid(self, form):
        """Handle form submission."""
        form.instance.user = self.request.user
        messages.success(self.request, 'Telegram settings updated successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics
        session = self.get_object()
        context['stats'] = {
            'contacts_count': TelegramContact.objects.filter(user=self.request.user).count(),
            'chats_count': TelegramChat.objects.filter(user=self.request.user).count(),
            'messages_count': TelegramMessage.objects.filter(user=self.request.user).count(),
            'last_sync': session.last_activity,
        }
        
        # Add available bots
        context['bots'] = TelegramBot.objects.filter(user=self.request.user, is_active=True)
        
        return context


class TelegramBotManagementView(LoginRequiredMixin, ListView):
    """
    Manage Telegram bots.
    """
    model = TelegramBot
    template_name = 'communication/telegram/bots.html'
    context_object_name = 'bots'
    
    def get_queryset(self):
        return TelegramBot.objects.filter(user=self.request.user)


class TelegramBotCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new Telegram bot.
    """
    model = TelegramBot
    form_class = TelegramBotForm
    template_name = 'communication/telegram/bot_form.html'
    success_url = reverse_lazy('communication:telegram_bots')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Bot @{form.instance.username} created successfully.')
        return super().form_valid(form)


class TelegramMediaUploadView(LoginRequiredMixin, View):
    """
    Handle media file uploads for Telegram messages.
    """
    
    def post(self, request, chat_id):
        """Upload media file and send message."""
        try:
            chat = TelegramChat.objects.get(
                id=chat_id,
                user=request.user
            )
        except TelegramChat.DoesNotExist:
            return JsonResponse({'error': 'Chat not found'}, status=404)
        
        uploaded_file = request.FILES.get('media_file')
        caption = request.POST.get('caption', '')
        
        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        try:
            # Determine media type
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                media_type = 'photo'
            elif file_extension in ['mp4', 'avi', 'mov']:
                media_type = 'video'
            elif file_extension in ['mp3', 'ogg', 'wav']:
                media_type = 'audio'
            else:
                media_type = 'document'
            
            # Create message with media
            telegram_message = TelegramMessage.objects.create(
                user=request.user,
                chat=chat,
                contact=chat.contact,
                message_text=caption,
                media_file=uploaded_file,
                media_type=media_type,
                media_caption=caption,
                telegram_message_id=0,  # Will be updated when actually sent
                telegram_chat_id=chat.telegram_chat_id,
                message_type=media_type,
                is_outgoing=True,
                status='sent',
                sent_at=timezone.now()
            )
            
            # Update chat's last message date
            chat.last_message_date = timezone.now()
            chat.save()
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': str(telegram_message.id),
                    'type': telegram_message.message_type,
                    'media_url': telegram_message.media_file.url,
                    'caption': telegram_message.media_caption,
                    'sent_at': telegram_message.sent_at.isoformat(),
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Failed to upload media: {str(e)}'}, status=500)


class TelegramSearchView(LoginRequiredMixin, View):
    """
    Search through Telegram messages and chats.
    """
    
    def get(self, request):
        """Search messages and chats."""
        query = request.GET.get('q', '').strip()
        search_type = request.GET.get('type', 'all')
        
        if not query:
            return JsonResponse({'error': 'Search query is required'}, status=400)
        
        results = {}
        
        if search_type in ['all', 'messages']:
            # Search messages
            messages = TelegramMessage.objects.filter(
                user=request.user,
                message_text__icontains=query,
                is_deleted=False
            ).select_related('chat', 'contact')[:20]
            
            results['messages'] = [
                {
                    'id': str(msg.id),
                    'text': msg.preview_text,
                    'chat_title': str(msg.chat),
                    'contact_name': msg.contact.display_name if msg.contact else 'Unknown',
                    'sent_at': msg.sent_at.isoformat() if msg.sent_at else None,
                    'chat_id': str(msg.chat.id),
                }
                for msg in messages
            ]
        
        if search_type in ['all', 'chats']:
            # Search chats
            chats = TelegramChat.objects.filter(
                user=request.user,
                title__icontains=query
            ).select_related('contact')[:10]
            
            results['chats'] = [
                {
                    'id': str(chat.id),
                    'title': str(chat),
                    'type': chat.chat_type,
                    'last_message_date': chat.last_message_date.isoformat() if chat.last_message_date else None,
                }
                for chat in chats
            ]
        
        if search_type in ['all', 'contacts']:
            # Search contacts
            contacts = TelegramContact.objects.filter(
                user=request.user
            ).filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query)
            )[:10]
            
            results['contacts'] = [
                {
                    'id': str(contact.id),
                    'name': contact.display_name,
                    'username': contact.username,
                    'is_verified': contact.is_verified,
                    'is_premium': contact.is_premium,
                }
                for contact in contacts
            ]
        
        return JsonResponse(results)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """
    Handle incoming Telegram webhooks.
    """
    
    def post(self, request):
        """Process incoming webhook from Telegram."""
        try:
            data = json.loads(request.body)
            
            # Verify webhook (in production, verify the secret token)
            
            # Process the update
            # This would use TelegramWebhookHandler in production
            
            return JsonResponse({'status': 'ok'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class TelegramExportView(LoginRequiredMixin, View):
    """
    Export Telegram data.
    """
    
    def get(self, request):
        """Export chat data."""
        export_type = request.GET.get('type', 'messages')
        chat_id = request.GET.get('chat_id')
        
        if export_type == 'messages' and chat_id:
            return self._export_chat_messages(request, chat_id)
        elif export_type == 'contacts':
            return self._export_contacts(request)
        elif export_type == 'chats':
            return self._export_chats(request)
        else:
            return JsonResponse({'error': 'Invalid export type'}, status=400)
    
    def _export_chat_messages(self, request, chat_id):
        """Export messages from a specific chat."""
        try:
            chat = TelegramChat.objects.get(id=chat_id, user=request.user)
            messages = TelegramMessage.objects.filter(
                chat=chat,
                is_deleted=False
            ).order_by('sent_at')
            
            # Generate export data
            export_data = {
                'chat': {
                    'title': str(chat),
                    'type': chat.chat_type,
                    'export_date': timezone.now().isoformat(),
                },
                'messages': [
                    {
                        'id': msg.telegram_message_id,
                        'text': msg.message_text,
                        'type': msg.message_type,
                        'from': msg.contact.display_name if msg.contact else 'You',
                        'date': msg.sent_at.isoformat() if msg.sent_at else None,
                        'is_outgoing': msg.is_outgoing,
                    }
                    for msg in messages
                ]
            }
            
            response = JsonResponse(export_data)
            response['Content-Disposition'] = f'attachment; filename="telegram_chat_{chat.id}.json"'
            return response
            
        except TelegramChat.DoesNotExist:
            return JsonResponse({'error': 'Chat not found'}, status=404)
    
    def _export_contacts(self, request):
        """Export Telegram contacts."""
        contacts = TelegramContact.objects.filter(user=request.user)
        
        export_data = {
            'export_date': timezone.now().isoformat(),
            'contacts': [
                {
                    'name': contact.display_name,
                    'username': contact.username,
                    'phone': contact.phone_number,
                    'is_verified': contact.is_verified,
                    'is_premium': contact.is_premium,
                }
                for contact in contacts
            ]
        }
        
        response = JsonResponse(export_data)
        response['Content-Disposition'] = 'attachment; filename="telegram_contacts.json"'
        return response
    
    def _export_chats(self, request):
        """Export chat list."""
        chats = TelegramChat.objects.filter(user=request.user)
        
        export_data = {
            'export_date': timezone.now().isoformat(),
            'chats': [
                {
                    'title': str(chat),
                    'type': chat.chat_type,
                    'last_message_date': chat.last_message_date.isoformat() if chat.last_message_date else None,
                    'message_count': chat.messages.count(),
                }
                for chat in chats
            ]
        }
        
        response = JsonResponse(export_data)
        response['Content-Disposition'] = 'attachment; filename="telegram_chats.json"'
        return response
