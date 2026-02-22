import os
import sys
import django
import logging

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from registration.models import SubscriptionPlan

def view_subscription_plans():
    """
    View all subscription plans and their pricing
    """
    try:
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
        
        print(f"Found {plans.count()} subscription plans:")
        print("=" * 60)
        
        for plan in plans:
            print(f"Plan: {plan.name}")
            print(f"Monthly Price: ${plan.price_monthly}")
            print(f"Annual Price: ${plan.price_annually}")
            
            # Calculate the savings
            monthly_annual = float(plan.price_monthly) * 12
            savings = monthly_annual - float(plan.price_annually)
            savings_percentage = (savings / monthly_annual) * 100
            
            print(f"Annual Savings: ${savings:.2f} ({savings_percentage:.1f}%)")
            print(f"Features: {plan.features}")
            print("-" * 60)
            
        return plans
    except Exception as e:
        logger.error(f"Error viewing subscription plans: {str(e)}")
        print(f"Error: {str(e)}")
        return None

if __name__ == '__main__':
    print("Checking subscription plans...")
    plans = view_subscription_plans()
    if plans:
        print("Subscription plans retrieved successfully!")
    else:
        print("Failed to retrieve subscription plans.")
