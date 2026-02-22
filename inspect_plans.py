import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from registration.models import SubscriptionPlan

def inspect_subscription_plans():
    """
    Inspect all subscription plans and their data
    """
    plans = SubscriptionPlan.objects.all()
    
    print(f"Found {plans.count()} subscription plans:")
    print("=" * 60)
    
    for i, plan in enumerate(plans):
        print(f"Plan {i+1}: {plan.name}")
        print(f"Description: {plan.description}")
        print(f"Monthly Price: {plan.price_monthly} (type: {type(plan.price_monthly)})")
        print(f"Annual Price: {plan.price_annually} (type: {type(plan.price_annually)})")
        print(f"Features: {plan.features} (type: {type(plan.features)})")
        print(f"Is Active: {plan.is_active}")
        print(f"Created At: {plan.created_at}")
        print(f"Updated At: {plan.updated_at}")
        print("-" * 60)

if __name__ == '__main__':
    inspect_subscription_plans()
