#!/usr/bin/env python3
"""
Debug script to examine the actual HTML form structure
"""

import requests
import time

def debug_form_html():
    """Debug the form HTML structure"""
    base_url = "http://localhost:5000"
    
    print("Debugging Form HTML Structure...")
    print("=" * 60)
    
    try:
        session = requests.Session()
        
        # Step 1: Load the create product form
        print("1. Loading create product form...")
        form_response = session.get(f"{base_url}/admin/product/new/?url=/admin/product/")
        
        if form_response.status_code == 200:
            print("✓ Create product form loaded successfully")
            
            # Step 2: Extract and analyze the form HTML
            html_content = form_response.text
            
            # Look for the form tag
            if '<form' in html_content:
                print("✓ Form tag found")
                
                # Look for form method and action
                import re
                form_match = re.search(r'<form[^>]*method=["\']([^"\']*)["\'][^>]*action=["\']([^"\']*)["\']', html_content)
                if form_match:
                    method = form_match.group(1)
                    action = form_match.group(2)
                    print(f"✓ Form method: {method}")
                    print(f"✓ Form action: {action}")
                else:
                    print("⚠ Form method/action not found")
                
                # Look for all input fields
                input_fields = re.findall(r'<input[^>]*name=["\']([^"\']*)["\'][^>]*>', html_content)
                print(f"✓ Found {len(input_fields)} input fields:")
                for field in input_fields:
                    print(f"  - {field}")
                
                # Look for textarea fields
                textarea_fields = re.findall(r'<textarea[^>]*name=["\']([^"\']*)["\'][^>]*>', html_content)
                print(f"✓ Found {len(textarea_fields)} textarea fields:")
                for field in textarea_fields:
                    print(f"  - {field}")
                
                # Look for select fields
                select_fields = re.findall(r'<select[^>]*name=["\']([^"\']*)["\'][^>]*>', html_content)
                print(f"✓ Found {len(select_fields)} select fields:")
                for field in select_fields:
                    print(f"  - {field}")
                
                # Look for hidden fields
                hidden_fields = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']*)["\'][^>]*>', html_content)
                print(f"✓ Found {len(hidden_fields)} hidden fields:")
                for field in hidden_fields:
                    print(f"  - {field}")
                
                # Look for CSRF token
                if 'csrf_token' in html_content:
                    print("✓ CSRF token field found")
                    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', html_content)
                    if csrf_match:
                        csrf_token = csrf_match.group(1)
                        print(f"✓ CSRF token value: {csrf_token[:20]}...")
                    else:
                        print("⚠ CSRF token field found but value not extracted")
                else:
                    print("⚠ No CSRF token field found")
                
                # Look for validation errors
                if 'This field is required' in html_content:
                    print("⚠ Form shows validation errors on load")
                else:
                    print("✓ Form loaded without validation errors")
                
                # Look for the actual form content
                print("\n2. Form field details:")
                
                # Check name field
                if 'name="name"' in html_content:
                    print("✓ Name field found")
                    # Check if it has a value
                    name_value_match = re.search(r'name="name"[^>]*value="([^"]*)"', html_content)
                    if name_value_match:
                        print(f"  - Name field value: '{name_value_match.group(1)}'")
                    else:
                        print("  - Name field has no value attribute")
                else:
                    print("✗ Name field not found")
                
                # Check description field
                if 'name="description"' in html_content:
                    print("✓ Description field found")
                    # Check if it has content
                    desc_content_match = re.search(r'<textarea[^>]*name="description"[^>]*>([^<]*)</textarea>', html_content)
                    if desc_content_match:
                        print(f"  - Description field content: '{desc_content_match.group(1)}'")
                    else:
                        print("  - Description field has no content")
                else:
                    print("✗ Description field not found")
                
                # Check category field
                if 'name="category"' in html_content:
                    print("✓ Category field found")
                    # Check if it has options
                    category_options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>', html_content)
                    if category_options:
                        print(f"  - Category field has {len(category_options)} options:")
                        for value, text in category_options:
                            print(f"    * {value}: {text}")
                    else:
                        print("  - Category field has no options")
                else:
                    print("✗ Category field not found")
                
            else:
                print("✗ No form tag found in HTML")
                
        else:
            print("✗ Could not load create product form")
            
    except Exception as e:
        print(f"✗ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Form HTML structure debugging completed!")

if __name__ == "__main__":
    # Wait a moment for the app to fully start
    print("Waiting for app to start...")
    time.sleep(3)
    debug_form_html()
