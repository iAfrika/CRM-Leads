# Dark Mode Testing Checklist

## Setup
- [ ] Start the Django development server
- [ ] Navigate to http://localhost:8000/site-admin/
- [ ] Login using admin credentials

## Basic Functionality
- [ ] Initial page loads with correct theme based on localStorage
- [ ] Dark mode toggle button is visible in the header
- [ ] Clicking the dark mode toggle button changes the theme
- [ ] Dark mode toggle icon changes between moon and sun icons
- [ ] Dark mode preference is saved when navigating between pages

## Visual Elements Testing
For each element, test in both light and dark modes:

### Navigation & Layout
- [ ] Sidebar background and text colors change appropriately
- [ ] Top navigation bar background and text colors change appropriately
- [ ] Active sidebar item is highlighted correctly in both modes
- [ ] Hover effects work correctly on sidebar items
- [ ] Page content area has appropriate background color
- [ ] Footer has appropriate styling

### Dashboard Elements
- [ ] Cards have correct background colors
- [ ] Card icons have appropriate styling and are visible
- [ ] Stat cards display correctly with readable text
- [ ] Recent actions display with proper contrast
- [ ] Action badges (add, change, delete) are clearly visible

### Forms and Inputs
- [ ] Form fields have appropriate styling
- [ ] Input text is readable against background
- [ ] Focused inputs have visible focus states
- [ ] Buttons maintain their color meaning and are clearly visible
- [ ] Checkboxes and radio buttons are functional and visible

### Tables
- [ ] Table headers have appropriate background color
- [ ] Table row alternating colors maintain readability
- [ ] Table text maintains good contrast with background
- [ ] Table hover effects work appropriately

### Alerts and Messages
- [ ] Success, error, warning, and info alerts are clearly visible
- [ ] Alert icons maintain proper color contrast
- [ ] Alert text is readable

## Responsive Testing
- [ ] Dark mode works correctly on mobile devices (use browser Dev Tools)
- [ ] Collapsed sidebar maintains appropriate styling in dark mode
- [ ] Mobile menu toggle works correctly in dark mode

## Browser Compatibility
Test dark mode in the following browsers:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

## Persistence Testing
- [ ] Toggle dark mode, then close and reopen the browser
- [ ] Verify that dark mode preference is remembered
- [ ] Clear localStorage and verify default theme is applied
- [ ] Check system preference detection works for dark/light modes

## Cross-Page Consistency
Visit each page and verify dark mode styling:
- [ ] Dashboard (`/site-admin/`)
- [ ] User Management (`/site-admin/users/`)
- [ ] Group Management (`/site-admin/groups/`)
- [ ] Any model list pages
- [ ] Any model detail pages
- [ ] Form pages (create/edit)
- [ ] Delete confirmation pages
- [ ] Dark Mode Test page (`/site-admin/dark_mode_test/`)

## Additional Tests
- [ ] Ensure no hardcoded colors are used that don't respect the theme
- [ ] Check for any flashing or FOUC (Flash of Unstyled Content) during theme changes
- [ ] Verify all font colors maintain WCAG AA contrast requirements (can use browser dev tools)
- [ ] Test keyboard navigation works well in dark mode

## Notes
- Document any issues found
- Record any areas that need attention or improvements
- Take screenshots of any problems for reference 