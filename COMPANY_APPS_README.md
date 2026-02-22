# Company-App Association System

## Overview
A complete system for associating companies with application modules in the CRM-Leads system.

## Features Implemented

### 1. Database Models
- **AppModule**: Represents available application modules
  - Fields: name, display_name, description, icon, is_active, requires_subscription, order
  - 12 default modules: Dashboard, Clients, Leads, Sales, Projects, Documents, Expenses, Purchases, Banking, Reports, People, Communication

- **CompanyApp**: Many-to-many relationship between companies and apps
  - Tracks which apps are enabled for each company
  - Records who enabled the app and when
  - Supports app-specific settings via JSONField

### 2. Management Commands
- `populate_app_modules`: Populates the database with default app modules
  ```bash
  python manage.py populate_app_modules
  ```

### 3. Views
- **company_apps(request, company_id)**: Manage apps for a company
  - Enable/disable apps
  - View all available modules
  - Filter by enabled status

### 4. URL Routes
- `/registration/company/<company_id>/apps/` - Manage company apps

### 5. Templates
- `registration/company_apps.html` - App management interface
  - Grid view of all available apps
  - Enable/disable buttons
  - Visual indicators for enabled apps
  - Premium badge for subscription-required apps

### 6. Middleware Integration
- **CompanyContextMiddleware** updated to:
  - Attach enabled apps list to request object
  - Available as `request.enabled_apps`

### 7. Context Processor
- **company_context** updated to:
  - Make enabled apps available in all templates
  - Available as `{{ enabled_apps }}` in templates

### 8. Admin Interface
- AppModule admin: Manage available modules
- CompanyApp admin: View and manage company-app associations
- Inline editing in Company admin

### 9. Auto-Enable Default Apps
- When a new company is registered, these apps are automatically enabled:
  - Dashboard
  - Clients Management
  - Leads Management
  - Sales Management
  - Document Management

## Usage

### For Administrators
1. Navigate to a company's details page
2. Click "Manage Apps" button
3. Enable or disable apps as needed

### For Developers
Check if an app is enabled in views:
```python
if 'sales' in request.enabled_apps:
    # Sales module is enabled
    pass
```

Check if an app is enabled in templates:
```django
{% if 'sales' in enabled_apps %}
    <a href="{% url 'sales:index' %}">Sales</a>
{% endif %}
```

### Adding New App Modules
1. Add to AppModule.APP_CHOICES in models.py
2. Run `python manage.py populate_app_modules`
3. Or add via Django admin

## Benefits
- ✅ Modular system - companies only see what they need
- ✅ Easy to extend with new modules
- ✅ Premium features can be gated behind subscriptions
- ✅ Automatic default configuration for new companies
- ✅ Per-company customization
- ✅ Admin-friendly interface

## Next Steps (Optional Enhancements)
1. Add app usage analytics
2. Implement app-specific permissions
3. Add app dependencies (e.g., Reports requires Sales)
4. Create app marketplace for third-party modules
5. Add app settings page for each module
6. Implement role-based app access
