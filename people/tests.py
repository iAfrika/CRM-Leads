from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Person, Role
import os

class PeopleViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test roles
        self.role1 = Role.objects.create(name='Customer')
        self.role2 = Role.objects.create(name='Supplier')
        
        # Create a test person
        self.person = Person.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='1234567890',
            telegram_username='@johndoe',
            address='123 Test St, Test City',
            registered_by=self.user
        )
        self.person.role.add(self.role1)
        
        # Set up the test client
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_people_list_view(self):
        """Test that the people list view loads correctly"""
        response = self.client.get(reverse('people:people_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/people_list.html')
        
        # Check if our CSS is included
        self.assertContains(response, 'people_styles.css')
        
        # Check if our person is in the response
        self.assertContains(response, 'John Doe')
    
    def test_person_detail_view(self):
        """Test that the person detail view loads correctly"""
        response = self.client.get(reverse('people:person_detail', args=[self.person.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/person_detail.html')
        
        # Check if our CSS is included
        self.assertContains(response, 'people_styles.css')
        
        # Check if person details are shown
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'john@example.com')
    
    def test_register_person_view(self):
        """Test that the register person view loads correctly"""
        response = self.client.get(reverse('people:register_person'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/register.html')
        
        # Check if our CSS is included
        self.assertContains(response, 'people_styles.css')
    
    def test_contact_people_view(self):
        """Test that the contact people view loads correctly"""
        response = self.client.get(reverse('people:contact_people'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/contact_form.html')
        
        # Check if our CSS is included
        self.assertContains(response, 'people_styles.css')
    
    def test_static_files_exist(self):
        """Test that our CSS file exists"""
        css_path = os.path.join('people', 'static', 'css', 'people_styles.css')
        self.assertTrue(os.path.exists(css_path) or os.path.exists(os.path.join('static', css_path)))
