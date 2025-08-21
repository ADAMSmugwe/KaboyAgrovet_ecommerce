#!/usr/bin/env python3
"""
Test script to verify Product creation form validation
"""

import requests
import time
import re

def test_product_creation():
    """Test Product creation form validation"""
    base_url = "http://localhost:5000"
    
    print("Testing Product Creation Form Validation...")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # Test 1: Get the create product form
        print("1. Loading create product form...")
        form_response = session.get(f"{base_url}/admin/product/new/?url=/admin/product/")
        
        if form_response.status_code == 200:
            print("✓ Create product form loaded successfully")
            
            # Check if all required fields are present
            required_fields = ['name', 'category', 'description']
            missing_fields = []
            for field in required_fields:
                if field not in form_response.text:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"✗ Missing fields: {missing_fields}")
            else:
                print("✓ All required fields found in form")
            
            # Test 2: Submit form with minimal data to trigger validation
            print("\n2. Testing form validation...")
            
            # Try submitting with missing required fields
            minimal_form_data = {
                'category': 'Fertilizer',
                # Intentionally omit name and description to test validation
            }
            
            submit_response = session.post(
                f"{base_url}/admin/product/new/?url=/admin/product/",
                data=minimal_form_data,
                allow_redirects=False
            )
            
            print(f"Form Submission Status: {submit_response.status_code}")
            
            # Check if there are validation errors in the response
            response_text = submit_response.text.lower()
            
            # Look for common validation error messages
            error_patterns = [
                r'field is required',
                r'this field is required',
                r'required',
                r'validation error',
                r'error',
                r'name.*required',
                r'description.*required'
            ]
            
            found_errors = []
            for pattern in error_patterns:
                matches = re.findall(pattern, response_text)
                if matches:
                    found_errors.extend(matches)
            
            if found_errors:
                print(f"✗ Found validation errors: {list(set(found_errors))}")
                print("This indicates the form validation is working but rejecting incomplete data")
            else:
                print("✓ No validation errors found in response")
            
            # Test 3: Submit form with complete data
            print("\n3. Testing complete form submission...")
            
            complete_form_data = {
                'name': 'Test Product',
                'category': 'Fertilizer',
                'description': 'This is a test product description'
            }
            
            complete_submit_response = session.post(
                f"{base_url}/admin/product/new/?url=/admin/product/",
                data=complete_form_data,
                allow_redirects=False
            )
            
            print(f"Complete Form Submission Status: {complete_submit_response.status_code}")
            
            if complete_submit_response.status_code in [200, 302, 303]:
                print("✓ Complete form submission successful")
            else:
                print(f"✗ Complete form submission failed")
                print(f"Response content: {complete_submit_response.text[:300]}...")
                
        else:
            print("✗ Could not load create product form")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
    
    print("\n" + "=" * 60)
    print("Product creation test completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    test_product_creation()
