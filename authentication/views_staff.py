from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from authentication.models import Profile
from django.contrib import messages
from django.db.models import Q
from leads.models import Lead
from projects.models import Project
from documents.models import Document
from people.models import Person
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@login_required
def staff_workspace(request):
    """
    Staff workspace view that only shows items specific to the current profile.
    This is an isolated view that only shows items the admin has allowed for this profile.
    """
    # Check if profile is in session
    profile_id = request.session.get('profile_id')
    role = request.session.get('user_role', 'staff')
    
    # Debug: print the session contents
    logger.info(f"Session contents: {request.session.items()}")
    logger.info(f"Staff workspace accessed by user: {request.user.username}, role: {role}, is_superuser: {request.user.is_superuser}")
    
    # If no profile selected, redirect to profile selection
    if not profile_id:
        messages.error(request, "Please select a profile to continue.")
        return redirect('authentication:profile_selection')
        
    # If role is administrator, offer to switch to admin dashboard
    if role == 'administrator':
        # We'll still show the staff workspace but with a notice and link
        messages.info(request, "You're viewing the staff workspace. Would you like to switch to the admin dashboard?")
        # We'll add a context variable to show admin dashboard link
    
    try:
        # Get profile
        profile = Profile.objects.get(id=profile_id, user=request.user)
        
        # Get the person associated with this user
        # The error shows Person doesn't have 'user' field - using the name fields instead
        try:
            # Try to find person by matching first_name and last_name with user's data
            person = Person.objects.filter(
                first_name=request.user.first_name,
                last_name=request.user.last_name
            ).first()
            
            if not person:
                # If not found by name, try by email
                if hasattr(request.user, 'email') and request.user.email:
                    person = Person.objects.filter(email=request.user.email).first()
                    
            # Log the person found or not
            if person:
                logger.info(f"Found person: {person.first_name} {person.last_name}")
            else:
                logger.warning(f"No person found for user: {request.user.username}")
        except Exception as e:
            logger.error(f"Error finding person: {str(e)}")
            person = None
            
        # Get data specific to this profile
        context = {}
        
        # Get leads assigned to this person - with safe handling
        context['assigned_leads'] = []
        try:
            if person:
                # Check if Lead model has assigned_to field that accepts Person objects
                try:
                    # Test if the filter works
                    Lead.objects.filter(assigned_to=person).exists()
                    context['assigned_leads'] = Lead.objects.filter(
                        assigned_to=person
                    ).order_by('-created_at')[:5]
                except Exception as e:
                    logger.warning(f"Cannot filter leads by assigned_to: {str(e)}")
                    # Try alternative: filter by created_by if available
                    if hasattr(Lead, 'created_by'):
                        context['assigned_leads'] = Lead.objects.filter(
                            created_by=request.user
                        ).order_by('-created_at')[:5]
        except Exception as e:
            logger.error(f"Error retrieving leads: {str(e)}")
            
        # Get projects this person is involved with - with safe handling
        context['assigned_projects'] = []
        try:
            if person:
                project_filters = Q()
                
                # Check if Project model has team_members that accepts Person objects
                try:
                    # Test if the filter works
                    Project.objects.filter(team_members=person).exists()
                    project_filters |= Q(team_members=person)
                except Exception as e:
                    logger.warning(f"Cannot filter projects by team_members: {str(e)}")
                
                # Check if Project model has project_manager that accepts Person objects
                try:
                    # Test if the filter works
                    Project.objects.filter(project_manager=person).exists()
                    project_filters |= Q(project_manager=person)
                except Exception as e:
                    logger.warning(f"Cannot filter projects by project_manager: {str(e)}")
                
                # Apply the filters if any were added
                if project_filters:
                    context['assigned_projects'] = Project.objects.filter(
                        project_filters
                    ).distinct().order_by('-created_at')[:5]
                else:
                    # Fallback - get projects related to user if possible
                    if hasattr(Project, 'created_by'):
                        context['assigned_projects'] = Project.objects.filter(
                            created_by=request.user
                        ).order_by('-created_at')[:5]
        except Exception as e:
            logger.error(f"Error retrieving projects: {str(e)}")
            
        # Get recent documents - safely handle filters
        try:
            document_filters = Q()
            
            # If the Document model has created_by field that's a User
            if hasattr(Document, 'created_by'):
                document_filters |= Q(created_by=request.user)
            
            # If we have a person and Document has client with primary_contact
            if person:
                # Check if these relationships exist before adding to the filter
                try:
                    # Test one document to see if the filter works
                    Document.objects.filter(client__primary_contact=person).exists()
                    document_filters |= Q(client__primary_contact=person)
                except Exception as e:
                    logger.warning(f"Cannot filter documents by client__primary_contact: {str(e)}")
            
            # Apply the filters if any were added
            if document_filters:
                context['recent_documents'] = Document.objects.filter(document_filters).order_by('-created_at')[:5]
            else:
                # Fallback - just get the most recent documents
                context['recent_documents'] = Document.objects.all().order_by('-created_at')[:5]
                
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            context['recent_documents'] = []
        
        # Get tasks due soon
        context['upcoming_tasks'] = []  # Implement this based on your task model
        
        # Get recent activities
        context['recent_activities'] = []  # Implement this based on your activity model
        
        # Add profile to context
        context['profile'] = profile
        context['person'] = person
        context['user_role'] = role
        
        # Explicitly check if role is administrator (handle both 'admin' and 'administrator')
        is_admin = (role == 'administrator' or role == 'admin')
        logger.info(f"User role: {role}, Is administrator: {is_admin}")
        context['show_admin_link'] = is_admin
        
        return render(request, 'authentication/staff_workspace.html', context)
        
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('authentication:profile_selection')
