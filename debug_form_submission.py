#!/usr/bin/env python3
"""
Debug script to examine form HTML and submission process
"""

import requests
import time

def debug_form_submission():
    """Debug the form submission process"""
    base_url = "http://localhost:5000"
    
    print("Debugging Form Submission Process...")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # Step 1: Load the create product form
        print("1. Loading create product form...")
        form_response = session.get(f"{base_url}/admin/product/new/?url=/admin/product/")
        
        if form_response.status_code == 200:
            print("✓ Create product form loaded successfully")
            
            # Extract CSRF token if present
            csrf_token = None
            if 'name="csrf_token"' in form_response.text:
                import re
                csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', form_response.text)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"✓ Found CSRF token: {csrf_token[:20]}...")
                else:
                    print("⚠ CSRF token field found but value not extracted")
            else:
                print("⚠ No CSRF token field found")
            
            # Step 2: Submit form with data
            print("\n2. Submitting form with test data...")
            test_data = {
                'name': 'Test Product - Debug Test',
                'description': 'This is a test product for debugging',
                'category': 'Fertilizer',
                'image_url': 'test-image.jpg'
            }
            
            # Add CSRF token if found
            if csrf_token:
                test_data['csrf_token'] = csrf_token
                print("✓ Added CSRF token to submission data")
            
            # Submit the form
            submit_response = session.post(
                f"{base_url}/admin/product/new/?url=/admin/product/",
                data=test_data,
                allow_redirects=False
            )
            
            print(f"Form submission status: {submit_response.status_code}")
            print(f"Response headers: {dict(submit_response.headers)}")
            
            # Step 3: Analyze the response
            if submit_response.status_code == 200:
                print("⚠ Form returned 200 (form re-rendered)")
                
                # Check for validation errors
                if 'This field is required' in submit_response.text:
                    print("✗ Form shows validation errors")
                    
                    # Check if our data is still in the form
                    if 'Test Product - Debug Test' in submit_response.text:
                        print("✓ Form data is retained (good)")
                    else:
                        print("✗ Form data was cleared (problem!)")
                        
                    if 'This is a test product for debugging' in submit_response.text:
                        print("✓ Description is retained (good)")
                    else:
                        print("✗ Description was cleared (problem!)")
                        
                    if 'Fertilizer' in submit_response.text:
                        print("✓ Category selection is retained (good)")
                    else:
                        print("✗ Category selection was cleared (problem!)")
                        
                    # Look for the actual form fields to see what's happening
                    if 'value="Test Product - Debug Test"' in submit_response.text:
                        print("✓ Name field has correct value attribute")
                    else:
                        print("✗ Name field missing or has wrong value")
                        
                    if '>This is a test product for debugging</textarea>' in submit_response.text:
                        print("✓ Description field has correct content")
                    else:
                        print("✗ Description field missing or has wrong content")
                        
                else:
                    print("✓ Form submitted without validation errors")
                    
            elif submit_response.status_code == 302:
                print("✓ Form submitted successfully with redirect")
                redirect_url = submit_response.headers.get('Location')
                print(f"Redirect URL: {redirect_url}")
                
            else:
                print(f"✗ Unexpected response status: {submit_response.status_code}")
                
        else:
            print("✗ Could not load create product form")
            
    except Exception as e:
        print(f"✗ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Form submission debugging completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    debug_form_submission()
