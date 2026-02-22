#!/usr/bin/env python
"""
Dark Mode Testing Script

This script tests the dark mode functionality across the site admin interface
to ensure it works consistently on all pages and UI elements.
"""

import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Settings
BASE_URL = "http://localhost:8000"
ADMIN_URL = f"{BASE_URL}/site-admin/"
USERNAME = "admin"
PASSWORD = "admin"
PAGES_TO_TEST = [
    "",  # Dashboard 
    "users/",
    "groups/",
    "dark_mode_test/"  # Our test page
]

def setup_driver():
    """Set up the WebDriver for testing."""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up WebDriver: {e}")
        sys.exit(1)

def login(driver):
    """Log in to the admin site."""
    try:
        driver.get(f"{ADMIN_URL}")
        
        # Check if we're already on the dashboard (already logged in)
        if "Dashboard" in driver.title:
            print("Already logged in, proceeding with tests")
            return True
            
        # Enter credentials
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)
        
        # Submit form
        password_field.submit()
        
        # Wait for login to complete
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "admin-sidebar"))
        )
        
        print("Successfully logged in")
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False

def test_dark_mode_toggle(driver):
    """Test toggling dark mode on and off."""
    try:
        # Find dark mode toggle button
        dark_mode_toggle = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "dark-mode-toggle"))
        )
        
        # Get initial state
        html_element = driver.find_element(By.TAG_NAME, "html")
        initial_state = "dark-mode" in html_element.get_attribute("class")
        print(f"Initial dark mode state: {'On' if initial_state else 'Off'}")
        
        # Toggle dark mode
        dark_mode_toggle.click()
        time.sleep(1)  # Wait for transition
        
        # Verify toggle worked
        html_element = driver.find_element(By.TAG_NAME, "html")
        new_state = "dark-mode" in html_element.get_attribute("class")
        print(f"Dark mode toggled to: {'On' if new_state else 'Off'}")
        
        if new_state == initial_state:
            print("ERROR: Dark mode toggle failed - state did not change")
            return False
            
        # Toggle back
        dark_mode_toggle.click()
        time.sleep(1)  # Wait for transition
        
        # Verify toggle back worked
        html_element = driver.find_element(By.TAG_NAME, "html")
        final_state = "dark-mode" in html_element.get_attribute("class")
        print(f"Dark mode toggled back to: {'On' if final_state else 'Off'}")
        
        if final_state != initial_state:
            print("ERROR: Dark mode toggle failed - could not restore original state")
            return False
            
        return True
    except Exception as e:
        print(f"Error testing dark mode toggle: {e}")
        return False

def verify_dark_mode_persistence(driver, page_url):
    """Verify dark mode setting persists when navigating between pages."""
    try:
        # Turn on dark mode
        html_element = driver.find_element(By.TAG_NAME, "html")
        initial_state = "dark-mode" in html_element.get_attribute("class")
        
        if not initial_state:
            dark_mode_toggle = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "dark-mode-toggle"))
            )
            dark_mode_toggle.click()
            time.sleep(1)  # Wait for transition
        
        # Navigate to another page
        driver.get(f"{ADMIN_URL}{page_url}")
        time.sleep(2)  # Wait for page load
        
        # Verify dark mode persisted
        html_element = driver.find_element(By.TAG_NAME, "html")
        new_state = "dark-mode" in html_element.get_attribute("class")
        
        if not new_state:
            print(f"ERROR: Dark mode did not persist when navigating to {page_url}")
            return False
            
        print(f"Dark mode successfully persisted when navigating to {page_url}")
        return True
    except Exception as e:
        print(f"Error verifying dark mode persistence: {e}")
        return False

def take_screenshot(driver, name):
    """Take a screenshot of the current page."""
    try:
        screenshot_dir = "dark_mode_test_screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
            
        filename = f"{screenshot_dir}/{name}_{int(time.time())}.png"
        driver.save_screenshot(filename)
        print(f"Screenshot saved: {filename}")
    except Exception as e:
        print(f"Error taking screenshot: {e}")

def test_all_pages(driver):
    """Test dark mode on all specified pages."""
    success = True
    
    for page in PAGES_TO_TEST:
        page_url = f"{ADMIN_URL}{page}"
        print(f"\nTesting page: {page_url}")
        
        try:
            driver.get(page_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "admin-sidebar"))
            )
            
            # Test toggle
            if not test_dark_mode_toggle(driver):
                success = False
                
            # Test persistence
            if not verify_dark_mode_persistence(driver, page):
                success = False
                
            # Take screenshots in both modes
            html_element = driver.find_element(By.TAG_NAME, "html")
            is_dark = "dark-mode" in html_element.get_attribute("class")
            
            # Get light mode screenshot
            if is_dark:
                dark_mode_toggle = driver.find_element(By.CLASS_NAME, "dark-mode-toggle")
                dark_mode_toggle.click()
                time.sleep(1)
            take_screenshot(driver, f"{page.replace('/', '_')}_light")
            
            # Get dark mode screenshot
            dark_mode_toggle = driver.find_element(By.CLASS_NAME, "dark-mode-toggle")
            dark_mode_toggle.click()
            time.sleep(1)
            take_screenshot(driver, f"{page.replace('/', '_')}_dark")
            
        except Exception as e:
            print(f"Error testing page {page_url}: {e}")
            success = False
    
    return success

def main():
    print("Dark Mode Testing Tool")
    print("======================")
    
    driver = setup_driver()
    success = False
    
    try:
        if login(driver):
            success = test_all_pages(driver)
    finally:
        driver.quit()
    
    if success:
        print("\n✅ All dark mode tests passed successfully!")
        return 0
    else:
        print("\n❌ Some dark mode tests failed. Check the output for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 