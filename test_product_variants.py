#!/usr/bin/env python3
"""
Test script to debug product variants API issue
"""

import requests
import json

def test_product_variants_api():
    """Test the product variants API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("Testing Product Variants API...")
    print("=" * 50)
    
    # Test 1: Debug endpoint
    print("\n1. Testing debug endpoint...")
    try:
        response = requests.get(f"{base_url}/api/debug/product-variants")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Regular product variants endpoint
    print("\n2. Testing regular product variants endpoint...")
    try:
        response = requests.get(f"{base_url}/api/product-variants")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Number of variants returned: {len(data)}")
            if data:
                print(f"First variant: {json.dumps(data[0], indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Admin product variants endpoint
    print("\n3. Testing admin product variants endpoint...")
    try:
        response = requests.get(f"{base_url}/api/admin/product-variants")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Number of variants returned: {len(data)}")
            if data:
                print(f"First variant: {json.dumps(data[0], indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Products endpoint
    print("\n4. Testing products endpoint...")
    try:
        response = requests.get(f"{base_url}/api/products")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Number of products returned: {len(data)}")
            if data:
                print(f"First product: {json.dumps(data[0], indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_product_variants_api()
