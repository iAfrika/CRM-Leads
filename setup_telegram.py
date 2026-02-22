#!/usr/bin/env python
"""
Telegram Setup Script for CRM-Leads
===================================

This script helps you set up the Telegram integration for your CRM system.

Prerequisites:
1. Create a Telegram app at https://my.telegram.org/apps
2. Get your API ID and API Hash
3. Optionally create a bot at @BotFather for bot functionality

Usage:
    python setup_telegram.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from django.contrib.auth import get_user_model
from communication.models import TelegramSession, TelegramBot

User = get_user_model()

def setup_telegram_session():
    """Set up a Telegram session for a user"""
    print("=== Telegram Session Setup ===")
    print("\nBefore proceeding, make sure you have:")
    print("1. Created an app at https://my.telegram.org/apps")
    print("2. Have your API ID and API Hash ready")
    print("3. Have access to your Telegram phone number")
    
    # Get user
    users = User.objects.all()
    if not users.exists():
        print("\nNo users found. Please create a user first:")
        print("python manage.py createsuperuser")
        return
    
    print(f"\nAvailable users:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.username} ({user.email})")
    
    while True:
        try:
            choice = int(input(f"\nSelect user (1-{users.count()}): ")) - 1
            if 0 <= choice < users.count():
                selected_user = users[choice]
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\nSetting up Telegram for: {selected_user.username}")
    
    # Get API credentials
    api_id = input("Enter your Telegram API ID: ").strip()
    api_hash = input("Enter your Telegram API Hash: ").strip()
    phone_number = input("Enter your phone number (with country code, e.g., +1234567890): ").strip()
    
    if not all([api_id, api_hash, phone_number]):
        print("All fields are required!")
        return
    
    # Create or update session
    session, created = TelegramSession.objects.get_or_create(
        user=selected_user,
        defaults={
            'phone_number': phone_number,
            'api_id': api_id,
            'api_hash': api_hash,
            'auto_sync_messages': True,
            'auto_sync_contacts': True,
            'sync_frequency': 300,  # 5 minutes
        }
    )
    
    if not created:
        session.phone_number = phone_number
        session.api_id = api_id
        session.api_hash = api_hash
        session.save()
    
    print(f"\n✅ Telegram session {'created' if created else 'updated'} successfully!")
    print(f"📱 Phone: {phone_number}")
    print(f"🔑 API ID: {api_id}")
    print(f"🔐 API Hash: {api_hash[:8]}...")
    
    print("\nNext steps:")
    print("1. Go to http://127.0.0.1:9000/communication/telegram/")
    print("2. Use the management command to authenticate:")
    print("   python manage.py telegram_client create_session")
    print("3. Follow the prompts to enter the verification code sent to your phone")

def setup_telegram_bot():
    """Set up a Telegram bot"""
    print("\n=== Telegram Bot Setup ===")
    print("\nTo create a bot:")
    print("1. Message @BotFather on Telegram")
    print("2. Use /newbot command")
    print("3. Follow the prompts to get your bot token")
    
    # Get user
    users = User.objects.all()
    if not users.exists():
        print("\nNo users found. Please create a user first.")
        return
    
    print(f"\nAvailable users:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.username} ({user.email})")
    
    while True:
        try:
            choice = int(input(f"\nSelect user (1-{users.count()}): ")) - 1
            if 0 <= choice < users.count():
                selected_user = users[choice]
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get bot details
    bot_name = input("Enter bot name: ").strip()
    bot_username = input("Enter bot username (without @): ").strip()
    bot_token = input("Enter bot token from @BotFather: ").strip()
    bot_description = input("Enter bot description (optional): ").strip()
    
    if not all([bot_name, bot_username, bot_token]):
        print("Name, username, and token are required!")
        return
    
    # Ensure username ends with 'bot'
    if not bot_username.lower().endswith('bot'):
        bot_username += 'bot'
    
    # Create bot
    bot, created = TelegramBot.objects.get_or_create(
        user=selected_user,
        username=bot_username,
        defaults={
            'name': bot_name,
            'token': bot_token,
            'description': bot_description,
            'is_active': True,
            'allowed_updates': ['message', 'callback_query'],
        }
    )
    
    if not created:
        bot.name = bot_name
        bot.token = bot_token
        bot.description = bot_description
        bot.save()
    
    print(f"\n✅ Telegram bot {'created' if created else 'updated'} successfully!")
    print(f"🤖 Name: {bot_name}")
    print(f"📛 Username: @{bot_username}")
    print(f"🔑 Token: {bot_token[:10]}...")
    
    print("\nYour bot is ready! You can now:")
    print("1. Test it by messaging @" + bot_username + " on Telegram")
    print("2. Configure webhooks in the admin panel")
    print("3. Use the bot API for automated responses")

def main():
    """Main setup function"""
    print("🚀 Telegram Integration Setup for CRM-Leads")
    print("=" * 50)
    
    while True:
        print("\nWhat would you like to set up?")
        print("1. Telegram User Session (for personal messaging)")
        print("2. Telegram Bot (for automated responses)")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            setup_telegram_session()
        elif choice == '2':
            setup_telegram_bot()
        elif choice == '3':
            print("\n👋 Setup complete! Enjoy your Telegram integration!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
