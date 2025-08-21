#!/usr/bin/env python3
"""
Test script to verify that form data is properly retained and saved
"""

import requests
import time
import re

def test_form_data_retention():
    """Test that form data is properly retained and saved"""
    base_url = "http://localhost:5000"
    
    print("Testing Form Data Retention and Saving...")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # Test 1: Load the create product form
        print("1. Loading create product form...")
        form_response = session.get(f"{base_url}/admin/product/new/?url=/admin/product/")
        
        if form_response.status_code == 200:
            print("✓ Create product form loaded successfully")
            
            # Test 2: Submit form with data
            print("\n2. Submitting form with test data...")
            test_data = {
                'name': 'Test Product - Data Retention Test',
                'description': 'This is a test product to verify data retention',
                'category': 'Fertilizer',
                'image_url': 'test-image.jpg'
            }
            
            # Submit the form
            submit_response = session.post(
                f"{base_url}/admin/product/new/?url=/admin/product/",
                data=test_data,
                allow_redirects=False
            )
            
            print(f"Form submission status: {submit_response.status_code}")
            
            if submit_response.status_code == 302:  # Redirect means success
                print("✓ Form submitted successfully with redirect")
                
                # Follow the redirect to see if we're on the list page
                redirect_url = submit_response.headers.get('Location')
                if redirect_url:
                    print(f"Redirecting to: {redirect_url}")
                    list_response = session.get(f"{base_url}{redirect_url}")
                    if list_response.status_code == 200:
                        print("✓ Successfully redirected to product list")
                        
                        # Check if our product appears in the list
                        if 'Test Product - Data Retention Test' in list_response.text:
                            print("✓ Product successfully saved and appears in list!")
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
                    print("✗ Form shows validation errors despite having data")
                    
                    # Check if our data is still in the form
                    if 'Test Product - Data Retention Test' in submit_response.text:
                        print("✓ Form data is retained (good)")
                    else:
                        print("✗ Form data was cleared (this is the problem!)")
                        
                    if 'Fertilizer' in submit_response.text:
                        print("✓ Category selection is retained (good)")
                    else:
                        print("✗ Category selection was cleared (this is the problem!)")
                else:
                    print("✓ Form submitted without validation errors")
                    
            else:
                print(f"✗ Unexpected response status: {submit_response.status_code}")
                
        else:
            print("✗ Could not load create product form")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
    
    print("\n" + "=" * 60)
    print("Form data retention test completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    test_form_data_retention()
