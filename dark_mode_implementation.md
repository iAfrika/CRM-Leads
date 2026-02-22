# Dark Mode Implementation

## Overview

This document outlines the implementation of dark mode across the site admin dashboard. The dark mode has been designed to be:

1. **Consistent** across all pages and UI elements
2. **Accessible** with proper contrast ratios
3. **Persistent** using localStorage
4. **System-aware** with support for `prefers-color-scheme` media query
5. **Smooth** with transitions between themes

## Technical Implementation

### CSS Variables Approach

The dark mode implementation uses CSS variables to maintain consistency. All color values are defined as variables in the root element, with overrides for dark mode.

```css
:root {
    /* Light mode theme variables */
    --body-bg: #f8f9fa;
    --body-color: #333;
    /* ...more variables */
}

html.dark-mode {
    /* Dark mode theme variables */
    --body-bg: #1a202c;
    --body-color: #e2e8f0;
    /* ...more variables */
}
```

This approach allows all elements to automatically adapt to the current theme.

### JavaScript Toggle Functionality

Dark mode is toggled by adding or removing the `.dark-mode` class on the `<html>` element. The preference is saved to localStorage:

```javascript
function toggleDarkMode(isDark) {
    // Apply dark mode class to the html element
    document.documentElement.classList.toggle('dark-mode', isDark);
    
    // Update icon
    // ...
    
    // Store preference
    localStorage.setItem('site_admin_dark_mode', isDark);
}
```

### System Preference Detection

The implementation checks for system dark mode preference using the `prefers-color-scheme` media query:

```javascript
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
```

## File Structure

The dark mode implementation spans several files:

- **admin_base.css** - Contains the main CSS variables and theme definitions
- **admin_dashboard.css** - Dashboard-specific styling with theme support
- **admin.js** - Contains the JavaScript for toggling dark mode
- **base.html** - Contains the dark mode toggle button in the header

## Testing

A comprehensive testing process has been implemented:

1. **Automated Tests** - The `test_dark_mode.py` script uses Selenium to verify dark mode functionality
2. **Manual Testing** - The `dark_mode_testing_checklist.md` provides a thorough list of things to test
3. **Test Page** - A dedicated test page at `/site-admin/dark_mode_test/` shows all UI elements in both modes

## Accessibility Considerations

Special attention has been paid to ensure dark mode is accessible:

- Text contrast ratios meet WCAG AA requirements
- Interactive elements maintain their affordances in dark mode
- Focus states are clearly visible in both light and dark modes
- No elements rely solely on color to convey information

## Browser Compatibility

The dark mode implementation has been tested in:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Future Enhancements

Potential improvements for the future:

1. Add animation when toggling between modes
2. Allow users to set a scheduled time for automatic dark/light mode switching
3. Add additional theme options beyond just light and dark 