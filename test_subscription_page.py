import os
import sys
import django
import requests
import logging
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from registration.models import SubscriptionPlan

def test_subscription_plans():
    """
    Test the subscription plans to ensure they have the correct prices
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
            print("-" * 60)
            
        # Verify Basic Plan
        basic_plan = plans.filter(name='Basic Plan').first()
        if basic_plan and float(basic_plan.price_monthly) == 10.0 and float(basic_plan.price_annually) == 96.0:
            print("✓ Basic Plan pricing is correct")
        else:
            print("✗ Basic Plan pricing is incorrect")
            
        # Verify Professional Plan
        prof_plan = plans.filter(name='Professional Plan').first()
        if prof_plan and float(prof_plan.price_monthly) == 20.0 and float(prof_plan.price_annually) == 192.0:
            print("✓ Professional Plan pricing is correct")
        else:
            print("✗ Professional Plan pricing is incorrect")
            
        # Verify Enterprise Plan
        ent_plan = plans.filter(name='Enterprise Plan').first()
        if ent_plan and float(ent_plan.price_monthly) == 50.0 and float(ent_plan.price_annually) == 480.0:
            print("✓ Enterprise Plan pricing is correct")
        else:
            print("✗ Enterprise Plan pricing is incorrect")
            
        return True
    except Exception as e:
        logger.error(f"Error testing subscription plans: {str(e)}")
        print(f"Error: {str(e)}")
        return False

if __name__ == '__main__':
    print("Testing subscription plans...")
    if test_subscription_plans():
        print("Subscription plans test completed successfully!")
    else:
        print("Subscription plans test failed.")
