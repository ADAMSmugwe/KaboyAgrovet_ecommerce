#!/usr/bin/env python3
"""
Test script to test form validation manually without Flask-Admin
"""

import sys
import os

# Add the current directory to Python path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_form_validation():
    """Test form validation manually"""
    print("Testing Form Validation Manually...")
    print("=" * 60)
    
    try:
        # Import the app and create a test context
        from app import app, Product, db
        
        with app.app_context():
            print("✓ App context created successfully")
            
            # Test 1: Check if we can access the database
            print("\n1. Testing database access...")
            try:
                products = Product.query.all()
                print(f"✓ Database accessible - found {len(products)} existing products")
            except Exception as e:
                print(f"✗ Database access failed: {e}")
                return
            
            # Test 2: Test form validation manually
            print("\n2. Testing form validation manually...")
            try:
                from app import ProductForm
                
                # Create a form with valid data
                form = ProductForm()
                form.name.data = 'Test Product Manual'
                form.description.data = 'Testing manual validation'
                form.category.data = 'Fertilizer'
                form.image_url.data = 'test.jpg'
                
                print("✓ Form created with test data")
                
                # Test validation
                if form.validate():
                    print("✓ Form validation passed")
                    
                    # Test 3: Try to create a product manually
                    print("\n3. Testing manual product creation...")
                    try:
                        # Create the product
                        product = Product(
                            name=form.name.data,
                            description=form.description.data,
                            category=form.category.data,
                            image_url=form.image_url.data
                        )
                        
                        # Add to database
                        db.session.add(product)
                        db.session.commit()
                        
                        print("✓ Product created successfully in database!")
                        print(f"  - ID: {product.id}")
                        print(f"  - Name: {product.name}")
                        print(f"  - Category: {product.category}")
                        
                        # Clean up - delete the test product
                        db.session.delete(product)
                        db.session.commit()
                        print("✓ Test product cleaned up")
                        
                    except Exception as e:
                        print(f"✗ Manual product creation failed: {e}")
                        db.session.rollback()
                        
                else:
                    print("✗ Form validation failed")
                    print("Validation errors:")
                    for field, errors in form.errors.items():
                        print(f"  - {field}: {errors}")
                        
            except Exception as e:
                print(f"✗ Form validation test failed: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Manual form validation test completed!")

if __name__ == "__main__":
    test_form_validation()
