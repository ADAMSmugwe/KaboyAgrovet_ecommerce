#!/usr/bin/env python3
"""
Test script to verify stock level field validation
"""

import requests
import time

def test_stock_level_validation():
    """Test stock level field validation"""
    base_url = "http://localhost:5000"
    
    print("Testing Stock Level Field Validation...")
    print("=" * 50)
    
    # Test 1: Get the edit form
    try:
        session = requests.Session()
        form_response = session.get(f"{base_url}/admin/productvariant/edit/?id=2&url=/admin/productvariant/")
        
        if form_response.status_code == 200:
            print("✓ Edit form loaded successfully")
            
            # Check if stock_level field is present
            if 'stock_level' in form_response.text:
                print("✓ Stock level field found in form")
            else:
                print("✗ Stock level field not found in form")
            
            # Test 2: Submit form with stock level
            form_data = {
                'product_id': '1',  # Assuming product ID 1 exists
                'quantity_value': '10.0',
                'quantity_unit': 'kg',
                'selling_price': '500.0',
                'stock_level': '100',  # This should work
                'supplier': 'Test Supplier'
            }
            
            submit_response = session.post(
                f"{base_url}/admin/productvariant/edit/?id=2&url=/admin/productvariant/",
                data=form_data,
                allow_redirects=False
            )
            
            print(f"Form Submission with Stock Level: {submit_response.status_code}")
            if submit_response.status_code in [200, 302, 303]:
                print("✓ Form submission with stock level successful")
            else:
                print(f"✗ Form submission failed with status: {submit_response.status_code}")
                print(f"Response content: {submit_response.text[:300]}...")
                
        else:
            print("✗ Could not load edit form")
            
    except Exception as e:
        print(f"✗ Error testing stock level validation: {e}")
    
    print("\n" + "=" * 50)
    print("Stock level validation test completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    test_stock_level_validation()
