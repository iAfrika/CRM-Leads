import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from registration.models import SubscriptionPlan
from decimal import Decimal

def update_subscription_plans():
    """
    Update subscription plans with the following pricing:
    - Basic: $10/month, $96/year (20% off)
    - Professional: $20/month, $192/year (20% off)
    - Enterprise: $50/month, $480/year (20% off)
    """
    # Calculate annual prices with 20% discount
    basic_annual = Decimal('10') * 12 * Decimal('0.8')
    professional_annual = Decimal('20') * 12 * Decimal('0.8')
    enterprise_annual = Decimal('50') * 12 * Decimal('0.8')
    
    # Update or create Basic plan
    basic_plan, created = SubscriptionPlan.objects.update_or_create(
        name='Basic Plan',
        defaults={
            'description': 'Perfect for small businesses and startups',
            'price_monthly': Decimal('10.00'),
            'price_annually': basic_annual,
            'features': [
                'Up to 3 Users',
                'Client Management',
                'Quotes & Invoices',
                'Basic Reporting',
                '500 Transactions/month'
            ],
            'is_active': True
        }
    )
    
    # Update or create Professional plan
    professional_plan, created = SubscriptionPlan.objects.update_or_create(
        name='Professional Plan',
        defaults={
            'description': 'Designed for growing businesses',
            'price_monthly': Decimal('20.00'),
            'price_annually': professional_annual,
            'features': [
                'Up to 10 Users',
                'Client Management',
                'Quotes & Invoices',
                'Unlimited Transactions',
                'Inventory Management',
                'Advanced Reporting'
            ],
            'is_active': True
        }
    )
    
    # Update or create Enterprise plan
    enterprise_plan, created = SubscriptionPlan.objects.update_or_create(
        name='Enterprise Plan',
        defaults={
            'description': 'For established businesses with complex needs',
            'price_monthly': Decimal('50.00'),
            'price_annually': enterprise_annual,
            'features': [
                'Unlimited Users',
                'Client Management',
                'Quotes & Invoices',
                'Unlimited Transactions',
                'Inventory Management',
                'Advanced Reporting',
                'Banking Module',
                'API Access'
            ],
            'is_active': True
        }
    )
    
    print(f"Basic Plan: ${basic_plan.price_monthly}/month, ${basic_plan.price_annually}/year")
    print(f"Professional Plan: ${professional_plan.price_monthly}/month, ${professional_plan.price_annually}/year")
    print(f"Enterprise Plan: ${enterprise_plan.price_monthly}/month, ${enterprise_plan.price_annually}/year")
    
    return {
        'basic_plan': basic_plan,
        'professional_plan': professional_plan,
        'enterprise_plan': enterprise_plan
    }

if __name__ == '__main__':
    print("Updating subscription plans...")
    plans = update_subscription_plans()
    print("Subscription plans updated successfully!")
