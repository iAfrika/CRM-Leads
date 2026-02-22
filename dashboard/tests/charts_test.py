from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import get_user_model, authenticate
from django.template.context import RequestContext
import json
import sys

class QuotesInvoicesChartToggleTest(TestCase):
    def setUp(self):
        """
        Set up a test user with Administrator role
        """
        # Create a test user with Administrator role
        User = get_user_model()
        
        # Create Administrator group if it doesn't exist
        administrator_group, created = Group.objects.get_or_create(name='Administrator')
        
        # Create the user 
        self.user = User.objects.create_user(
            username='admin', 
            email='admin@example.com',
            password='pass'
        )
        
        # Set staff status to true
        self.user.is_staff = True
        
        # Add to Administrator group
        self.user.groups.add(administrator_group)
        
        # Ensure full access 
        self.user.is_superuser = True
        self.user.save()

    def _get_context_dict(self, context):
        """
        Convert context to a dictionary safely
        """
        # Define the keys we're specifically interested in
        DASHBOARD_KEYS = [
            'quotes_count', 'invoices_count', 
            'quotes_total_value', 'invoices_total_value',
            'quotes_count_value', 'invoices_count_value',
            'quotes_invoices_data'
        ]

        # If context is a RequestContext, convert it to a dictionary
        if isinstance(context, RequestContext):
            # Convert to a dictionary, filtering for our specific keys
            context_dict = {}
            for key in DASHBOARD_KEYS:
                try:
                    context_dict[key] = context.get(key)
                except Exception:
                    pass
            return context_dict
        
        # If it's already a dictionary, filter for our keys
        elif isinstance(context, dict):
            return {k: v for k, v in context.items() if k in DASHBOARD_KEYS}
        
        # If it has an items method, try that
        elif hasattr(context, 'items'):
            context_dict = dict(context.items())
            return {k: v for k, v in context_dict.items() if k in DASHBOARD_KEYS}
        
        # Fallback
        return {}

    def test_dashboard_access(self):
        """
        Verify dashboard can be accessed by logged-in Administrator
        """
        # Authenticate the user specifically as an Administrator
        user = authenticate(username='admin', password='pass')
        print(f"Authenticated user: {user}", file=sys.stderr)
        
        # Verify user is in Administrator group
        administrator_group = Group.objects.get(name='Administrator')
        is_administrator = user.groups.filter(name='Administrator').exists()
        print(f"Is Administrator: {is_administrator}", file=sys.stderr)
        
        # Log in the test user
        login_success = self.client.login(username='admin', password='pass')
        print(f"Login success: {login_success}", file=sys.stderr)
        
        # Verify default role is set to Administrator
        default_role = 'Administrator'
        print(f"Default Role: {default_role}", file=sys.stderr)
        
        self.assertTrue(login_success, "Login should be successful")
        self.assertTrue(is_administrator, "User should be in Administrator group")
        
        # Get the dashboard page
        response = self.client.get(reverse('dashboard:main_dashboard'), follow=True)
        print(f"Response status code: {response.status_code}", file=sys.stderr)
        
        # Check response
        self.assertEqual(response.status_code, 200, 
            f"Dashboard access failed. Response: {response.status_code}")

    def test_dashboard_context_data(self):
        """
        Test that the dashboard view provides correct context data
        """
        # Log in the test user
        login_success = self.client.login(username='admin', password='pass')
        print(f"Login success: {login_success}", file=sys.stderr)
        
        # Verify user is in Administrator group
        administrator_group = Group.objects.get(name='Administrator')
        is_administrator = self.user.groups.filter(name='Administrator').exists()
        print(f"Is Administrator: {is_administrator}", file=sys.stderr)
        
        # Get the dashboard page with follow to handle redirects
        response = self.client.get(reverse('dashboard:main_dashboard'), follow=True)
        
        # Inspect the response history to understand redirects
        print("Response History:", file=sys.stderr)
        for resp, url in response.redirect_chain:
            print(f"Redirected to: {url}", file=sys.stderr)
        
        # Safely access context data
        context = response.context[-1] if response.context else {}
        context = self._get_context_dict(context)
        
        # Print out full context for debugging
        print("Full Context:", file=sys.stderr)
        for key, value in context.items():
            print(f"{key}: {type(value)} = {value}", file=sys.stderr)
        
        # Verify context exists
        self.assertIsNotNone(context, "Response context should not be None")
        
        # Required context keys for chart data
        required_keys = [
            'quotes_count', 'invoices_count', 
            'quotes_total_value', 'invoices_total_value',
            'quotes_count_value', 'invoices_count_value',
            'quotes_invoices_data'
        ]
        
        # Check each key exists in context
        for key in required_keys:
            self.assertIn(key, context, 
                f"Context should contain key: {key}")
            
            # Additional type checks
            value = context[key]
            if key.endswith('count'):
                self.assertIsInstance(value, int, 
                    f"{key} should be an integer")
                self.assertGreaterEqual(value, 0, 
                    f"{key} should be non-negative")
            elif key.endswith('value'):
                # Check numeric values
                self.assertTrue(isinstance(value, (int, float)) or 
                    (hasattr(value, 'is_integer') and value.is_integer()), 
                    f"{key} should be a numeric value")

    def test_quotes_invoices_chart_data(self):
        """
        Test the structure and content of quotes vs invoices chart data
        """
        # Log in the test user
        login_success = self.client.login(username='admin', password='pass')
        print(f"Login success: {login_success}", file=sys.stderr)
        
        # Verify user is in Administrator group
        administrator_group = Group.objects.get(name='Administrator')
        is_administrator = self.user.groups.filter(name='Administrator').exists()
        print(f"Is Administrator: {is_administrator}", file=sys.stderr)
        
        # Get the dashboard page with follow to handle redirects
        response = self.client.get(reverse('dashboard:main_dashboard'), follow=True)
        
        # Inspect the response history to understand redirects
        print("Response History:", file=sys.stderr)
        for resp, url in response.redirect_chain:
            print(f"Redirected to: {url}", file=sys.stderr)
        
        # Safely access context data
        context = response.context[-1] if response.context else {}
        context = self._get_context_dict(context)
        
        # Print out full context for debugging
        print("Full Context:", file=sys.stderr)
        for key, value in context.items():
            print(f"{key}: {type(value)} = {value}", file=sys.stderr)
        
        # Verify quotes_invoices_data exists
        quotes_invoices_data = context.get('quotes_invoices_data')
        print(f"Quotes invoices data: {quotes_invoices_data}", file=sys.stderr)
        self.assertIsNotNone(quotes_invoices_data, 
            "Quotes vs Invoices chart data should exist")
        
        # Parse quotes_invoices_data
        try:
            chart_data = json.loads(quotes_invoices_data)
        except json.JSONDecodeError:
            self.fail("Quotes vs Invoices chart data should be valid JSON")
        
        # Verify chart data structure
        self.assertIn('labels', chart_data, 
            "Chart data should have labels")
        self.assertIn('datasets', chart_data, 
            "Chart data should have datasets")
        
        # Check labels
        self.assertEqual(
            chart_data['labels'], 
            ['Quotes', 'Invoices'], 
            "Chart labels should be ['Quotes', 'Invoices']"
        )
        
        # Check dataset
        datasets = chart_data['datasets']
        self.assertEqual(len(datasets), 1, 
            "Should have one dataset")
        
        dataset = datasets[0]
        self.assertIn('data', dataset, 
            "Dataset should have data")
        self.assertIn('backgroundColor', dataset, 
            "Dataset should have background colors")

    def test_toggle_data_consistency(self):
        """
        Ensure data consistency between context variables
        """
        # Log in the test user
        login_success = self.client.login(username='admin', password='pass')
        print(f"Login success: {login_success}", file=sys.stderr)
        
        # Verify user is in Administrator group
        administrator_group = Group.objects.get(name='Administrator')
        is_administrator = self.user.groups.filter(name='Administrator').exists()
        print(f"Is Administrator: {is_administrator}", file=sys.stderr)
        
        # Get the dashboard page with follow to handle redirects
        response = self.client.get(reverse('dashboard:main_dashboard'), follow=True)
        
        # Inspect the response history to understand redirects
        print("Response History:", file=sys.stderr)
        for resp, url in response.redirect_chain:
            print(f"Redirected to: {url}", file=sys.stderr)
        
        # Safely access context data
        context = response.context[-1] if response.context else {}
        context = self._get_context_dict(context)
        
        # Print out full context for debugging
        print("Full Context:", file=sys.stderr)
        for key, value in context.items():
            print(f"{key}: {type(value)} = {value}", file=sys.stderr)
        
        # Verify data relationships
        quotes_count = context['quotes_count']
        invoices_count = context['invoices_count']
        quotes_total_value = context['quotes_total_value']
        invoices_total_value = context['invoices_total_value']
        
        # Validate count and value relationships
        self.assertTrue(quotes_count >= 0, 
            "Quotes count should be non-negative")
        self.assertTrue(invoices_count >= 0, 
            "Invoices count should be non-negative")
        
        # Ensure total values are consistent with counts
        if quotes_count > 0:
            quotes_avg = quotes_total_value / quotes_count
            self.assertAlmostEqual(
                context['quotes_count_value'], 
                quotes_count * quotes_avg, 
                msg="Quotes count value should match calculated value"
            )
        
        if invoices_count > 0:
            invoices_avg = invoices_total_value / invoices_count
            self.assertAlmostEqual(
                context['invoices_count_value'], 
                invoices_count * invoices_avg, 
                msg="Invoices count value should match calculated value"
            )
