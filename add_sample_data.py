#!/usr/bin/env python3
"""
Script to add sample data to the database for testing
"""

from app import app, db, Product, ProductVariant
from datetime import datetime, timedelta

def add_sample_data():
    """Add sample products and variants to the database"""
    
    with app.app_context():
        # Check if we already have data
        existing_products = Product.query.count()
        existing_variants = ProductVariant.query.count()
        
        print(f"Current database state:")
        print(f"Products: {existing_products}")
        print(f"Variants: {existing_variants}")
        
        if existing_products > 0:
            print("Database already has data. Skipping sample data creation.")
            return
        
        print("Adding sample data...")
        
        # Create sample products
        products_data = [
            {
                'name': 'NPK Fertilizer',
                'category': 'Fertilizer',
                'description': 'High-quality NPK fertilizer for all crops',
                'image_url': 'https://example.com/npk.jpg'
            },
            {
                'name': 'Organic Pesticide',
                'category': 'Pesticide',
                'description': 'Natural pesticide safe for organic farming',
                'image_url': 'https://example.com/pesticide.jpg'
            },
            {
                'name': 'Maize Seeds',
                'category': 'Seed',
                'description': 'High-yield maize seeds for optimal harvest',
                'image_url': 'https://example.com/maize.jpg'
            },
            {
                'name': 'Chicken Feed',
                'category': 'Feed',
                'description': 'Nutritious feed for poultry farming',
                'image_url': 'https://example.com/feed.jpg'
            }
        ]
        
        created_products = []
        for product_data in products_data:
            product = Product(**product_data)
            db.session.add(product)
            created_products.append(product)
        
        db.session.commit()
        print(f"Created {len(created_products)} products")
        
        # Create sample variants for each product
        variants_data = [
            # NPK Fertilizer variants
            {
                'product': created_products[0],
                'quantity_value': 25.0,
                'quantity_unit': 'kg',
                'selling_price': 2500.0,
                'buying_price': 2000.0,
                'stock_level': 50,
                'expiry_date': datetime.utcnow() + timedelta(days=365),
                'supplier': 'Agro Supplies Ltd'
            },
            {
                'product': created_products[0],
                'quantity_value': 50.0,
                'quantity_unit': 'kg',
                'selling_price': 4500.0,
                'buying_price': 3500.0,
                'stock_level': 25,
                'expiry_date': datetime.utcnow() + timedelta(days=365),
                'supplier': 'Agro Supplies Ltd'
            },
            # Organic Pesticide variants
            {
                'product': created_products[1],
                'quantity_value': 5.0,
                'quantity_unit': 'L',
                'selling_price': 800.0,
                'buying_price': 600.0,
                'stock_level': 30,
                'expiry_date': datetime.utcnow() + timedelta(days=180),
                'supplier': 'Organic Solutions'
            },
            {
                'product': created_products[1],
                'quantity_value': 10.0,
                'quantity_unit': 'L',
                'selling_price': 1500.0,
                'buying_price': 1100.0,
                'stock_level': 15,
                'expiry_date': datetime.utcnow() + timedelta(days=180),
                'supplier': 'Organic Solutions'
            },
            # Maize Seeds variants
            {
                'product': created_products[2],
                'quantity_value': 2.0,
                'quantity_unit': 'kg',
                'selling_price': 300.0,
                'buying_price': 200.0,
                'stock_level': 100,
                'expiry_date': datetime.utcnow() + timedelta(days=730),
                'supplier': 'Seed Co Ltd'
            },
            {
                'product': created_products[2],
                'quantity_value': 5.0,
                'quantity_unit': 'kg',
                'selling_price': 700.0,
                'buying_price': 450.0,
                'stock_level': 50,
                'expiry_date': datetime.utcnow() + timedelta(days=730),
                'supplier': 'Seed Co Ltd'
            },
            # Chicken Feed variants
            {
                'product': created_products[3],
                'quantity_value': 25.0,
                'quantity_unit': 'kg',
                'selling_price': 1200.0,
                'buying_price': 900.0,
                'stock_level': 40,
                'expiry_date': datetime.utcnow() + timedelta(days=90),
                'supplier': 'Feed Masters'
            },
            {
                'product': created_products[3],
                'quantity_value': 50.0,
                'quantity_unit': 'kg',
                'selling_price': 2200.0,
                'buying_price': 1600.0,
                'stock_level': 20,
                'expiry_date': datetime.utcnow() + timedelta(days=90),
                'supplier': 'Feed Masters'
            }
        ]
        
        for variant_data in variants_data:
            product = variant_data.pop('product')
            variant = ProductVariant(product_id=product.id, **variant_data)
            db.session.add(variant)
        
        db.session.commit()
        print(f"Created {len(variants_data)} variants")
        
        # Verify the data
        final_products = Product.query.count()
        final_variants = ProductVariant.query.count()
        
        print(f"\nFinal database state:")
        print(f"Products: {final_products}")
        print(f"Variants: {final_variants}")
        
        print("\nSample data added successfully!")

if __name__ == "__main__":
    add_sample_data()
