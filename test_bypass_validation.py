#!/usr/bin/env python3
"""
Test script to bypass validation and see if the issue is in validation or data binding
"""

import requests
import time

def test_bypass_validation():
    """Test form submission by bypassing validation"""
    base_url = "http://localhost:5000"
    
    print("Testing Form Submission with Validation Bypass...")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # Step 1: Load the create product form
        print("1. Loading create product form...")
        form_response = session.get(f"{base_url}/admin/product/new/?url=/admin/product/")
        
        if form_response.status_code == 200:
            print("✓ Create product form loaded successfully")
            
            # Step 2: Submit form with COMPLETE data (should pass validation)
            print("\n2. Submitting form with COMPLETE data...")
            complete_data = {
                'name': 'Complete Test Product',
                'description': 'This is a complete test product with all fields filled',
                'category': 'Fertilizer',
                'image_url': 'complete-test.jpg'
            }
            
            # Submit the form
            submit_response = session.post(
                f"{base_url}/admin/product/new/?url=/admin/product/",
                data=complete_data,
                allow_redirects=False
            )
            
            print(f"Form submission status: {submit_response.status_code}")
            
            if submit_response.status_code == 302:
                print("✓ Form submitted successfully with redirect!")
                redirect_url = submit_response.headers.get('Location')
                print(f"Redirect URL: {redirect_url}")
                
                # Follow the redirect to see if we're on the list page
                if redirect_url:
                    list_response = session.get(f"{base_url}{redirect_url}")
                    if list_response.status_code == 200:
                        print("✓ Successfully redirected to product list")
                        
                        # Check if our product appears in the list
                        if 'Complete Test Product' in list_response.text:
                            print("✓ Product successfully saved and appears in list!")
                            print("🎉 SUCCESS: Form data binding and saving works correctly!")
                        else:
                            print("✗ Product not found in list after submission")
                    else:
                        print(f"✗ Failed to follow redirect: {list_response.status_code}")
                else:
                    print("✗ No redirect URL found")
                    
            elif submit_response.status_code == 200:
                print("⚠ Form returned 200 (form re-rendered)")
                
                # Check if there are validation errors
                if 'This field is required' in submit_response.text:
                    print("✗ Form shows validation errors despite having complete data")
                    print("This suggests the validation logic is broken")
                    
                    # Check if our data is still in the form
                    if 'Complete Test Product' in submit_response.text:
                        print("✓ Form data is retained (good)")
                    else:
                        print("✗ Form data was cleared (problem!)")
                        
                    if 'This is a complete test product with all fields filled' in submit_response.text:
                        print("✓ Description is retained (good)")
                    else:
                        print("✗ Description was cleared (problem!)")
                        
                    if 'Fertilizer' in submit_response.text:
                        print("✓ Category selection is retained (good)")
                    else:
                        print("✗ Category selection was cleared (problem!)")
                        
                else:
                    print("✓ Form submitted without validation errors")
                    
            else:
                print(f"✗ Unexpected response status: {submit_response.status_code}")
                
        else:
            print("✗ Could not load create product form")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Validation bypass test completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    test_bypass_validation()
