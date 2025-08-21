#!/usr/bin/env python3
"""
Test script to verify field validation and check for "field is required" errors
"""

import requests
import time
import re

def test_field_validation():
    """Test field validation and check for required field errors"""
    base_url = "http://localhost:5000"
    
    print("Testing Field Validation and Required Field Errors...")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # Test 1: Get the edit form
        print("1. Loading edit form...")
        form_response = session.get(f"{base_url}/admin/productvariant/edit/?id=2&url=/admin/productvariant/")
        
        if form_response.status_code == 200:
            print("✓ Edit form loaded successfully")
            
            # Check if all required fields are present
            required_fields = ['product_id', 'quantity_value', 'quantity_unit', 'selling_price', 'stock_level']
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
                'product_id': '1',
                # Intentionally omit other required fields to test validation
            }
            
            submit_response = session.post(
                f"{base_url}/admin/productvariant/edit/?id=2&url=/admin/productvariant/",
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
                r'stock.*level.*required',
                r'quantity.*required',
                r'price.*required'
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
                'product_id': '1',
                'quantity_value': '10.0',
                'quantity_unit': 'kg',
                'selling_price': '500.0',
                'stock_level': '100',
                'supplier': 'Test Supplier'
            }
            
            complete_submit_response = session.post(
                f"{base_url}/admin/productvariant/edit/?id=2&url=/admin/productvariant/",
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
            print("✗ Could not load edit form")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
    
    print("\n" + "=" * 60)
    print("Field validation test completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    test_field_validation()
