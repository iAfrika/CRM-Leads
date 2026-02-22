from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Client
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator

# Create your views here.

class ClientListView(ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'

class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'
    
    def render_to_response(self, context):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            client = context['client']
            return JsonResponse({
                'id': client.id,
                'name': client.name,
                'contact_person': client.contact_person,
                'email': client.email,
                'phone': client.phone,
                'address': client.address
            })
        return super().render_to_response(context)

class ClientCreateView(CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['name', 'initials', 'contact_person', 'email', 'phone', 'address', 'notes']
    success_url = reverse_lazy('clients:client_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get company initials from request (set by middleware)
        from registration.models import CompanyUser, Company
        
        company_initials = 'CC'
        if self.request.user.is_authenticated:
            # Try to get from request.company first
            if hasattr(self.request, 'company') and self.request.company:
                print(f"DEBUG: Company from request: {self.request.company.name}, Initials: '{self.request.company.initials}'")
                if self.request.company.initials:
                    company_initials = self.request.company.initials
            else:
                print("DEBUG: No company in request, trying session")
                # Fallback: get from session
                active_company_id = self.request.session.get('active_company_id')
                print(f"DEBUG: Session company ID: {active_company_id}")
                if active_company_id:
                    try:
                        company = Company.objects.get(id=active_company_id)
                        print(f"DEBUG: Company from DB: {company.name}, Initials: '{company.initials}'")
                        if company.initials:
                            company_initials = company.initials
                    except Company.DoesNotExist:
                        print("DEBUG: Company not found in DB")
                        pass
        
        print(f"DEBUG: Final company_initials: '{company_initials}'")
        
        # Calculate the next client ID using company initials
        last_client = Client.objects.order_by('-id').first()
        if last_client and last_client.client_id:
            try:
                # Handle format without dash (e.g., CC0001)
                import re
                numbers = re.findall(r'\d+', last_client.client_id)
                last_number = int(numbers[-1]) if numbers else 0
                next_number = last_number + 1
            except (IndexError, ValueError):
                next_number = 1
        else:
            next_number = 1
        context['next_client_id'] = f"{company_initials}{next_number:04d}"
        print(f"DEBUG: Next client ID will be: {context['next_client_id']}")
        return context
    
    def form_valid(self, form):
        # Get company initials
        from registration.models import Company
        
        company_initials = 'CC'
        if self.request.user.is_authenticated:
            # Try to get from request.company first
            if hasattr(self.request, 'company') and self.request.company and self.request.company.initials:
                company_initials = self.request.company.initials
            else:
                # Fallback: get from session
                active_company_id = self.request.session.get('active_company_id')
                if active_company_id:
                    try:
                        company = Company.objects.get(id=active_company_id)
                        if company.initials:
                            company_initials = company.initials
                    except Company.DoesNotExist:
                        pass
        
        # Generate client_id before saving
        last_client = Client.objects.order_by('-id').first()
        if last_client and last_client.client_id:
            try:
                import re
                numbers = re.findall(r'\d+', last_client.client_id)
                last_number = int(numbers[-1]) if numbers else 0
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        form.instance.client_id = f"{company_initials}{next_number:04d}"
        return super().form_valid(form)

class ClientUpdateView(UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['name', 'initials', 'contact_person', 'email', 'phone', 'address', 'notes']
    success_url = reverse_lazy('clients:client_list')

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

