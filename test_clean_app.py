#!/usr/bin/env python3
"""
Test script for app_clean.py
"""

import requests
import json
import time

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing API endpoints...")
    
    # Test product variants endpoint
    try:
        response = requests.get(f"{base_url}/api/product-variants")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Product variants API working - Found {len(data)} variants")
            if data:
                print(f"   Sample variant: {data[0]['product_name']} - {data[0]['quantity_value']}{data[0]['quantity_unit']}")
        else:
            print(f"❌ Product variants API failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Product variants API error: {e}")
    
    # Test products endpoint
    try:
        response = requests.get(f"{base_url}/api/products")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Products API working - Found {len(data)} products")
            if data:
                print(f"   Sample product: {data[0]['name']} - {data[0]['category']}")
        else:
            print(f"❌ Products API failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Products API error: {e}")
    
    # Test search functionality
    try:
        response = requests.get(f"{base_url}/api/product-variants?search=NPK")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search API working - Found {len(data)} results for 'NPK'")
        else:
            print(f"❌ Search API failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Search API error: {e}")

def test_admin_access():
    """Test admin access"""
    base_url = "http://localhost:5000"
    
    print("\n🔐 Testing admin access...")
    
    try:
        response = requests.get(f"{base_url}/admin/")
        if response.status_code == 200:
            print("✅ Admin page accessible")
        elif response.status_code == 302:
            print("✅ Admin page redirecting to login (expected)")
        else:
            print(f"❌ Admin page failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin access error: {e}")

if __name__ == "__main__":
    print("🚀 Starting tests for Kaboy Agrovet Clean App...")
    print("Make sure the app is running on http://localhost:5000")
    
    # Wait a moment for the app to be ready
    time.sleep(2)
    
    test_api_endpoints()
    test_admin_access()
    
    print("\n✨ Test completed!")
    print("\n📋 Next steps:")
    print("1. Open http://localhost:5000/admin-login")
    print("2. Login with username: admin, password: admin123")
    print("3. Test the Manual Sales functionality")
    print("4. Check all admin sections are working") 