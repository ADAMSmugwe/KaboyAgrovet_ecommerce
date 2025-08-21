#!/usr/bin/env python3
"""
Test script to verify autocomplete attributes are added to form fields
"""

import requests
import time
import re

def test_autocomplete_attributes():
    """Test that autocomplete attributes are added to form fields"""
    base_url = "http://localhost:5000"
    
    print("Testing Autocomplete Attributes in Forms...")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # Test 1: Check Product creation form
        print("1. Checking Product creation form...")
        product_form_response = session.get(f"{base_url}/admin/product/new/?url=/admin/product/")
        
        if product_form_response.status_code == 200:
            print("✓ Product creation form loaded successfully")
            
            # Check for autocomplete attributes
            form_html = product_form_response.text
            
            # Look for autocomplete attributes in form fields
            autocomplete_pattern = r'autocomplete=["\']([^"\']+)["\']'
            autocomplete_matches = re.findall(autocomplete_pattern, form_html)
            
            if autocomplete_matches:
                print(f"✓ Found autocomplete attributes: {list(set(autocomplete_matches))}")
                
                # Check specific fields
                if 'autocomplete="off"' in form_html:
                    print("✓ Found autocomplete='off' for general fields")
                if 'autocomplete="name"' in form_html:
                    print("✓ Found autocomplete='name' for name fields")
                if 'autocomplete="email"' in form_html:
                    print("✓ Found autocomplete='email' for email fields")
            else:
                print("✗ No autocomplete attributes found")
            
            # Check specific field types
            field_checks = [
                ('name', 'autocomplete'),
                ('category', 'autocomplete'),
                ('description', 'autocomplete'),
                ('image_url', 'autocomplete')
            ]
            
            for field_name, attr_name in field_checks:
                if f'{attr_name}=' in form_html:
                    print(f"✓ {field_name} field has {attr_name} attribute")
                else:
                    print(f"✗ {field_name} field missing {attr_name} attribute")
                    
        else:
            print("✗ Could not load Product creation form")
        
        # Test 2: Check ProductVariant edit form
        print("\n2. Checking ProductVariant edit form...")
        variant_form_response = session.get(f"{base_url}/admin/productvariant/edit/?id=2&url=/admin/productvariant/")
        
        if variant_form_response.status_code == 200:
            print("✓ ProductVariant edit form loaded successfully")
            
            # Check for autocomplete attributes
            variant_form_html = variant_form_response.text
            
            # Look for autocomplete attributes in form fields
            variant_autocomplete_matches = re.findall(autocomplete_pattern, variant_form_html)
            
            if variant_autocomplete_matches:
                print(f"✓ Found autocomplete attributes: {list(set(variant_autocomplete_matches))}")
                
                # Check specific fields
                if 'autocomplete="off"' in variant_form_html:
                    print("✓ Found autocomplete='off' for general fields")
                if 'autocomplete="organization"' in variant_form_html:
                    print("✓ Found autocomplete='organization' for supplier field")
            else:
                print("✗ No autocomplete attributes found in ProductVariant form")
            
            # Check specific field types
            variant_field_checks = [
                ('product_id', 'autocomplete'),
                ('quantity_value', 'autocomplete'),
                ('quantity_unit', 'autocomplete'),
                ('selling_price', 'autocomplete'),
                ('stock_level', 'autocomplete'),
                ('supplier', 'autocomplete')
            ]
            
            for field_name, attr_name in variant_field_checks:
                if f'{attr_name}=' in variant_form_html:
                    print(f"✓ {field_name} field has {attr_name} attribute")
                else:
                    print(f"✗ {field_name} field missing {attr_name} attribute")
                    
        else:
            print("✗ Could not load ProductVariant edit form")
        
        # Test 3: Check Order creation form
        print("\n3. Checking Order creation form...")
        order_form_response = session.get(f"{base_url}/admin/order/new/?url=/admin/order/")
        
        if order_form_response.status_code == 200:
            print("✓ Order creation form loaded successfully")
            
            # Check for autocomplete attributes
            order_form_html = order_form_response.text
            
            # Look for autocomplete attributes in form fields
            order_autocomplete_matches = re.findall(autocomplete_pattern, order_form_html)
            
            if order_autocomplete_matches:
                print(f"✓ Found autocomplete attributes: {list(set(order_autocomplete_matches))}")
                
                # Check specific fields
                if 'autocomplete="name"' in order_form_html:
                    print("✓ Found autocomplete='name' for customer name")
                if 'autocomplete="email"' in order_form_html:
                    print("✓ Found autocomplete='email' for customer email")
                if 'autocomplete="tel"' in order_form_html:
                    print("✓ Found autocomplete='tel' for customer phone")
                if 'autocomplete="street-address"' in order_form_html:
                    print("✓ Found autocomplete='street-address' for delivery address")
            else:
                print("✗ No autocomplete attributes found in Order form")
                
        else:
            print("✗ Could not load Order creation form")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
    
    print("\n" + "=" * 60)
    print("Autocomplete attributes test completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    test_autocomplete_attributes()
