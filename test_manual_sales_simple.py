#!/usr/bin/env python3
"""
Simple test for manual sales functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app_simple_fixed import app, db, Product, ProductVariant
    
    print("🌱 Testing Manual Sales...")
    
    with app.app_context():
        # Test database connection
        try:
            db.engine.execute("SELECT 1")
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
        
        # Test model creation
        try:
            # Create a test product
            test_product = Product(
                name="Test Fertilizer",
                category="Fertilizer",
                description="This is a test fertilizer product"
            )
            db.session.add(test_product)
            db.session.commit()
            print("✅ Product creation successful")
            
            # Create a test variant
            test_variant = ProductVariant(
                product_id=test_product.id,
                quantity_value=1.0,
                quantity_unit="kg",
                selling_price=100.0,
                buying_price=80.0,
                stock_level=10
            )
            db.session.add(test_variant)
            db.session.commit()
            print("✅ Product variant creation successful")
            
            # Test API endpoints
            with app.test_client() as client:
                # Test product variants API
                response = client.get('/api/product-variants?search=fertilizer')
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"✅ Product variants API working - found {len(data)} variants")
                else:
                    print(f"❌ Product variants API failed - status {response.status_code}")
            
            # Clean up test data
            db.session.delete(test_variant)
            db.session.delete(test_product)
            db.session.commit()
            print("✅ Test data cleaned up successfully")
            
            print("\n🎉 Manual sales test completed!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            db.session.rollback()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}") 