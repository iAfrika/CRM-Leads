from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse
from decimal import Decimal
from .models import Account, Transaction, Debt, Tax
from .forms import AccountCreationForm, DepositForm, WithdrawForm, TransferForm
from project_management.models import Project
import uuid
import random
import string

@login_required
def dashboard(request):
    """
    Display the banking dashboard with account overview, recent transactions, and active debts.
    """
    accounts = Account.objects.filter(owner_id=request.user.id, is_active=True)
    total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        account__owner_id=request.user.id
    ).order_by('-timestamp')[:10]
    
    # Get active debts
    active_debts = Debt.objects.filter(
        account__owner_id=request.user.id,
        is_active=True
    )
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'recent_transactions': recent_transactions,
        'active_debts': active_debts,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/dashboard.html', context)

@login_required
def account_detail(request, account_number):
    """
    Display details for a specific account, including recent transactions.
    """
    account = get_object_or_404(Account, account_number=account_number, owner_id=request.user.id)
    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')[:20]
    
    context = {
        'account': account,
        'transactions': transactions,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/account_detail.html', context)

@login_required
def create_account(request):
    """
    Link a company bank account for tracking.
    """
    company = getattr(request, 'company', None)
    
    if request.method == 'POST':
        form = AccountCreationForm(request.POST, user=request.user, company=company)
        if form.is_valid():
            account = form.save()
            messages.success(
                request, 
                f'Bank account linked successfully! Account number: {account.account_number}'
            )
            return redirect('banking:account_detail', account_number=account.account_number)
        else:
            # If form is not valid, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = AccountCreationForm(user=request.user, company=company)
    
    context = {
        'form': form,
        'active_tab': 'banking',
    }
    return render(request, 'banking/create_account.html', context)

@login_required
def deposit(request, account_number):
    """
    Deposit funds into an account.
    """
    account = get_object_or_404(Account, account_number=account_number, owner_id=request.user.id)
    
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description')
            
            try:
                account.deposit(amount, description)
                messages.success(request, f'Successfully deposited ${amount} to your account.')
                return redirect('banking:account_detail', account_number=account_number)
            except ValueError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = DepositForm()
    
    context = {
        'account': account,
        'form': form,
        'active_tab': 'banking',
    }
    return render(request, 'banking/deposit.html', context)

@login_required
def withdraw(request, account_number):
    """
    Withdraw funds from an account.
    """
    account = get_object_or_404(Account, account_number=account_number, owner_id=request.user.id)
    
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description')
            
            try:
                account.withdraw(amount, description)
                messages.success(request, f'Successfully withdrew ${amount} from your account.')
                return redirect('banking:account_detail', account_number=account_number)
            except ValueError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = WithdrawForm()
    
    context = {
        'account': account,
        'form': form,
        'active_tab': 'banking',
    }
    return render(request, 'banking/withdraw.html', context)

@login_required
def transfer(request, account_number):
    """
    Transfer funds from one account to another.
    """
    source_account = get_object_or_404(Account, account_number=account_number, owner_id=request.user.id)
    
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            destination_account_number = form.cleaned_data['destination_account']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description')
            
            try:
                destination_account = Account.objects.get(account_number=destination_account_number)
                source_account.transfer(destination_account, amount, description)
                messages.success(request, f'Successfully transferred ${amount} to account {destination_account_number}.')
                return redirect('banking:account_detail', account_number=account_number)
            except Account.DoesNotExist:
                messages.error(request, 'Destination account not found.')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = TransferForm()
    
    context = {
        'account': source_account,
        'form': form,
        'active_tab': 'banking',
    }
    return render(request, 'banking/transfer.html', context)

@login_required
def transaction_history(request, account_number=None):
    """
    Display transaction history for a specific account or all accounts.
    """
    if account_number:
        account = get_object_or_404(Account, account_number=account_number, owner_id=request.user.id)
        transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
        context = {
            'account': account, 
            'transactions': transactions,
            'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
        }
    else:
        transactions = Transaction.objects.filter(account__owner_id=request.user.id).order_by('-timestamp')
        context = {
            'transactions': transactions,
            'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
        }
    
    return render(request, 'banking/transaction_history.html', context)



@login_required
def payment(request, account_number):
    """
    Make a payment from an account.
    """
    account = get_object_or_404(Account, account_number=account_number, owner_id=request.user.id)
    
    if request.method == 'POST':
        payee = request.POST.get('payee')
        amount = Decimal(request.POST.get('amount', 0))
        description = request.POST.get('description')
        
        try:
            if amount <= 0:
                raise ValueError("Payment amount must be positive")
            if account.balance < amount:
                raise ValueError("Insufficient funds")
                
            account.balance -= amount
            account.save()
            
            Transaction.objects.create(
                account=account,
                transaction_type='PAYMENT_SENT',
                amount=amount,
                description=f"Payment to {payee}: {description}"
            )
            
            messages.success(request, f'Payment of ${amount} to {payee} was successful.')
            return redirect('banking:account_detail', account_number=account_number)
        except ValueError as e:
            messages.error(request, str(e))
    
    context = {
        'account': account,
        'active_tab': 'banking',  # Add this to highlight the banking tab in the navbar
    }
    return render(request, 'banking/payment.html', context)

@login_required
def report_list(request):
    """
    Display a list of reports.
    """
    # Logic to retrieve and display reports
    return render(request, 'reports/report_list.html', {
        'title': 'Report List'
    })
