from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Email, EmailRecipient
from .forms import EmailForm

class OutlookEmailInboxView(LoginRequiredMixin, View):
    def get(self, request):
        # Get inbox emails for the current user
        emails = Email.objects.filter(recipients__email=request.user.email).order_by('-sent_at')
        
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
        
        return render(request, 'communication/email/inbox_outlook.html', context)

class OutlookEmailSentView(LoginRequiredMixin, View):
    def get(self, request):
        # Get sent emails for the current user
        emails = Email.objects.filter(sender_email=request.user.email).order_by('-sent_at')
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients__email=request.user.email)
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
        
        return render(request, 'communication/email/inbox_outlook.html', context)

class OutlookEmailDraftsView(LoginRequiredMixin, View):
    def get(self, request):
        # Get draft emails for the current user
        emails = Email.objects.filter(sender_email=request.user.email, is_draft=True).order_by('-updated_at')
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients__email=request.user.email)
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
        
        return render(request, 'communication/email/inbox_outlook.html', context)

class OutlookEmailViewView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # Get the email to view
        email = get_object_or_404(Email, pk=pk)
        
        # Mark as read if it's a received email
        if not email.is_read and email.recipients.filter(email=request.user.email).exists():
            email.is_read = True
            email.save()
        
        # Get all emails based on the current tab
        if email.sender_email == request.user.email and email.is_draft:
            active_tab = 'drafts'
            emails = Email.objects.filter(sender_email=request.user.email, is_draft=True).order_by('-updated_at')
        elif email.sender_email == request.user.email:
            active_tab = 'sent'
            emails = Email.objects.filter(sender_email=request.user.email, is_draft=False).order_by('-sent_at')
        else:
            active_tab = 'inbox'
            emails = Email.objects.filter(recipients__email=request.user.email).order_by('-sent_at')
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients__email=request.user.email)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        context = {
            'active_tab': active_tab,
            'emails': emails,
            'current_email': email,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/view_outlook.html', context)

class OutlookEmailComposeView(LoginRequiredMixin, View):
    def get(self, request):
        # Initialize form
        form = EmailForm()
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients__email=request.user.email)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        context = {
            'active_tab': 'compose',
            'form': form,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/compose_outlook.html', context)
    
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
                
                # Save recipients
                for recipient in form.cleaned_data['recipients']:
                    EmailRecipient.objects.create(email=email, recipient_email=recipient.email)
                
                messages.success(request, 'Email saved as draft.')
                return redirect('communication:email_drafts_outlook')
            else:
                # Sending the email
                email.is_draft = False
                email.save()
                
                # Save recipients
                for recipient in form.cleaned_data['recipients']:
                    EmailRecipient.objects.create(email=email, recipient_email=recipient.email)
                
                # Here you would actually send the email using your email backend
                
                messages.success(request, 'Email sent successfully.')
                return redirect('communication:email_sent_outlook')
        
        # Form is invalid
        context = {
            'active_tab': 'compose',
            'form': form,
            'unread_count': Email.objects.filter(recipients__email=request.user.email, is_read=False).count()
        }
        
        return render(request, 'communication/email/compose_outlook.html', context)

class OutlookEmailDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        email = get_object_or_404(Email, pk=pk)
        
        # Simple soft delete by marking as deleted
        email.is_deleted = True
        email.save()
        
        messages.success(request, 'Email moved to trash.')
        
        # Redirect based on the source
        redirect_to = request.POST.get('redirect_to', 'inbox')
        if redirect_to == 'sent':
            return redirect('communication:email_sent_outlook')
        elif redirect_to == 'drafts':
            return redirect('communication:email_drafts_outlook')
        else:
            return redirect('communication:email_inbox_outlook') 