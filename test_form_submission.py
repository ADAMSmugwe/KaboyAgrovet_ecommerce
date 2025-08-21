#!/usr/bin/env python3
"""
Test script to verify form submission functionality
"""

import requests
import time

def test_form_submission():
    """Test form submission functionality"""
    base_url = "http://localhost:5000"
    
    print("Testing Form Submission...")
    print("=" * 50)
    
    # Test 1: Get the edit form to see if it loads properly
    try:
        response = requests.get(f"{base_url}/admin/productvariant/edit/?id=2&url=/admin/productvariant/")
        print(f"Edit Form Load: {response.status_code}")
        if response.status_code == 200:
            print("✓ Edit form loads successfully")
            
            # Check if the form contains the expected fields
            if 'product_id' in response.text and 'quantity_value' in response.text:
                print("✓ Form contains expected fields")
            else:
                print("✗ Form missing expected fields")
        else:
            print("✗ Edit form failed to load")
    except Exception as e:
        print(f"✗ Error loading edit form: {e}")
    
    # Test 2: Try to submit a form (this will help identify any remaining issues)
    try:
        # Get the form first to get any CSRF tokens
        session = requests.Session()
        form_response = session.get(f"{base_url}/admin/productvariant/edit/?id=2&url=/admin/productvariant/")
        
        if form_response.status_code == 200:
            print("✓ Form retrieved successfully for submission test")
            
            # Try to submit a minimal form update
            form_data = {
                'quantity_value': '10.0',
                'stock_level': '50',
                'selling_price': '500.0'
            }
            
            # Submit the form
            submit_response = session.post(
                f"{base_url}/admin/productvariant/edit/?id=2&url=/admin/productvariant/",
                data=form_data,
                allow_redirects=False
            )
            
            print(f"Form Submission Test: {submit_response.status_code}")
            if submit_response.status_code in [200, 302, 303]:
                print("✓ Form submission appears to work")
            else:
                print(f"✗ Form submission returned status: {submit_response.status_code}")
                print(f"Response content: {submit_response.text[:200]}...")
        else:
            print("✗ Could not retrieve form for submission test")
            
    except Exception as e:
        print(f"✗ Error testing form submission: {e}")
    
    print("\n" + "=" * 50)
    print("Form submission test completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    test_form_submission()
