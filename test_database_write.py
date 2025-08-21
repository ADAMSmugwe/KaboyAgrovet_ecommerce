#!/usr/bin/env python3
"""
Test script to check if the database is writable and can create products
"""

import requests
import time

def test_database_write():
    """Test if the database is writable"""
    base_url = "http://localhost:5000"
    
    print("Testing Database Write Capability...")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # Step 1: Check if we can access the admin interface
        print("1. Testing admin interface access...")
        admin_response = session.get(f"{base_url}/admin/")
        
        if admin_response.status_code == 200:
            print("✓ Admin interface accessible")
        else:
            print(f"✗ Admin interface not accessible: {admin_response.status_code}")
            return
        
        # Step 2: Check if we can access the product list
        print("\n2. Testing product list access...")
        product_list_response = session.get(f"{base_url}/admin/product/")
        
        if product_list_response.status_code == 200:
            print("✓ Product list accessible")
            
            # Check if there are existing products
            if 'No products found' in product_list_response.text:
                print("  - No existing products found")
            else:
                print("  - Existing products found")
        else:
            print(f"✗ Product list not accessible: {product_list_response.status_code}")
            return
        
        # Step 3: Try to create a product with minimal data
        print("\n3. Testing product creation with minimal data...")
        
        # First, load the form to get any necessary tokens
        form_response = session.get(f"{base_url}/admin/product/new/?url=/admin/product/")
        
        if form_response.status_code == 200:
            print("✓ Create product form loaded")
            
            # Try to submit with minimal valid data
            minimal_data = {
                'name': 'Test Product DB Write',
                'description': 'Testing database write capability',
                'category': 'Fertilizer'
            }
            
            # Submit the form
            submit_response = session.post(
                f"{base_url}/admin/product/new/?url=/admin/product/",
                data=minimal_data,
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
                        if 'Test Product DB Write' in list_response.text:
                            print("✓ Product successfully saved and appears in list!")
                            print("🎉 SUCCESS: Database write is working!")
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
                    print("✗ Form shows validation errors despite having valid data")
                    print("This suggests a validation issue")
                else:
                    print("✓ Form submitted without validation errors")
                    
                # Check if our data is still in the form
                if 'Test Product DB Write' in submit_response.text:
                    print("✓ Form data is retained (good)")
                else:
                    print("✗ Form data was cleared (problem!)")
                    
            else:
                print(f"✗ Unexpected response status: {submit_response.status_code}")
                
        else:
            print("✗ Could not load create product form")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Database write test completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    test_database_write()
