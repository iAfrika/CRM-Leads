import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from registration.models import SubscriptionPlan
from decimal import Decimal

def update_subscription_plans_kes():
    """
    Update subscription plans with KES pricing:
    - Basic: KES 4,999/month
    - Professional: KES 9,999/month
    - Enterprise: KES 19,999/month
    With 20% discount for annual pricing
    """
    # Calculate annual prices with 20% discount
    basic_annual = Decimal('4999') * 12 * Decimal('0.8')
    professional_annual = Decimal('9999') * 12 * Decimal('0.8')
    enterprise_annual = Decimal('19999') * 12 * Decimal('0.8')
    
    # Update or create Basic plan
    basic_plan, created = SubscriptionPlan.objects.update_or_create(
        name='Basic Plan',
        defaults={
            'description': 'Perfect for small businesses and startups',
            'price_monthly': Decimal('4999'),
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
            'price_monthly': Decimal('9999'),
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
            'price_monthly': Decimal('19999'),
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
    
    print(f"Basic Plan: KES {basic_plan.price_monthly}/month, KES {basic_plan.price_annually}/year")
    print(f"Professional Plan: KES {professional_plan.price_monthly}/month, KES {professional_plan.price_annually}/year")
    print(f"Enterprise Plan: KES {enterprise_plan.price_monthly}/month, KES {enterprise_plan.price_annually}/year")
    
    return {
        'basic_plan': basic_plan,
        'professional_plan': professional_plan,
        'enterprise_plan': enterprise_plan
    }

if __name__ == '__main__':
    try:
        print("Updating subscription plans with KES pricing...")
        plans = update_subscription_plans_kes()
        print("Subscription plans updated successfully!")
    except Exception as e:
        print(f"Error updating subscription plans: {str(e)}")
