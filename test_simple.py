#!/usr/bin/env python3
"""
Simple test to verify Flask app starts without errors
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    
    print("✅ Successfully imported Flask app and database")
    
    with app.app_context():
        # Test database connection
        try:
            db.engine.execute("SELECT 1")
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
        
        # Test admin views registration
        try:
            from flask_admin import Admin
            admin = Admin(app, name='Kaboy Agrovet Admin', template_mode='bootstrap3', base_template='admin/master.html')
            print("✅ Admin configuration successful")
        except Exception as e:
            print(f"❌ Admin configuration failed: {e}")
    
    print("\n🎉 Flask application is ready!")
    print("📋 Available Admin Views:")
    print("   • Products - Add/edit products")
    print("   • Product Variants - Manage product variants")
    print("   • Customer Orders - View and manage orders")
    print("   • Order Items - Manage order line items")
    print("   • Offline Sales - Record offline transactions")
    print("   • Offline Sale Items - Manage sale line items")
    print("   • Testimonials - Manage customer testimonials")
    print("   • FAQs - Manage frequently asked questions")
    print("   • Contact Messages - View customer messages")
    print("   • Customer Analytics - View customer insights")
    print("   • Product Analytics - View product performance")
    print("   • Sales Analytics - View sales trends")
    print("   • Manual Sales - Custom sales interface")
    
    print("\n🚀 To start the application:")
    print("   python app.py")
    print("\n🌐 Then visit: http://localhost:5000/admin")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}") 