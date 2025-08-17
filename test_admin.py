#!/usr/bin/env python3
"""
Test script to verify admin interface functionality
"""

import requests
import time

def test_admin_interface():
    """Test the admin interface endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing Admin Interface...")
    print("=" * 50)
    
    # Test 1: Admin home page
    try:
        response = requests.get(f"{base_url}/admin/")
        print(f"Admin Home: {response.status_code}")
        if response.status_code == 200:
            print("✓ Admin home page accessible")
        else:
            print("✗ Admin home page not accessible")
    except Exception as e:
        print(f"✗ Error accessing admin home: {e}")
    
    # Test 2: Product Variants list
    try:
        response = requests.get(f"{base_url}/admin/productvariant/")
        print(f"Product Variants List: {response.status_code}")
        if response.status_code == 200:
            print("✓ Product variants list accessible")
        else:
            print("✗ Product variants list not accessible")
    except Exception as e:
        print(f"✗ Error accessing product variants: {e}")
    
    # Test 3: Try to access edit form (this should work now)
    try:
        response = requests.get(f"{base_url}/admin/productvariant/edit/?id=1&url=/admin/productvariant/")
        print(f"Product Variant Edit Form: {response.status_code}")
        if response.status_code == 200:
            print("✓ Product variant edit form accessible - Compatibility issue resolved!")
        else:
            print(f"✗ Product variant edit form returned status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error accessing product variant edit form: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    test_admin_interface() 