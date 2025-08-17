# app_simple_fixed.py - Fixed Flask Admin Setup with Working Manual Sales
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import BaseView, expose
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from wtforms.validators import DataRequired, Email
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'kaboy_agrovet.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['FLASK_ADMIN_CUSTOM_CSS'] = 'static/css/flask_admin_custom.css'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
CORS(app)

# --- MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    variants = db.relationship('ProductVariant', back_populates='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.id} {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'image_url': self.image_url,
            'variants': [variant.to_dict() for variant in self.variants]
        }
    
    @property
    def variants_count(self):
        return len(self.variants)

class ProductVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', back_populates='variants')
    quantity_value = db.Column(db.Float, nullable=False)
    quantity_unit = db.Column(db.String(20), nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    buying_price = db.Column(db.Float, nullable=True)
    stock_level = db.Column(db.Integer, default=0, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=True)
    supplier = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        product_name = self.product.name if self.product else "N/A"
        return f'<Variant {self.quantity_value}{self.quantity_unit} of {product_name} (Stock: {self.stock_level})>'

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product.name if self.product else "N/A",
            'quantity_value': self.quantity_value,
            'quantity_unit': self.quantity_unit,
            'selling_price': self.selling_price,
            'stock_level': self.stock_level,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'supplier': self.supplier
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(50), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', back_populates='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id} by {self.customer_name} - Total: {self.total_amount}>'

    def __str__(self):
        return f'Order {self.id} by {self.customer_name}'
    
    @property
    def items_count(self):
        return len(self.items)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order = db.relationship('Order', back_populates='items', lazy=True)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)
    variant = db.relationship('ProductVariant', backref='order_items', lazy=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        variant_info = f"{self.variant.product.name} ({self.variant.quantity_value}{self.variant.quantity_unit})" if self.variant and self.variant.product else "N/A"
        return f'<OrderItem {self.id} - {self.quantity} x {variant_info}>'

    def __str__(self):
        variant_info = f"{self.quantity} x {self.variant.product.name} ({self.variant.quantity_value}{self.variant.quantity_unit})" if self.variant and self.variant.product else "N/A"
        return f"{self.quantity} x {variant_info} @ KSh {self.price_at_purchase:.2f}"

class OfflineSale(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(100), nullable=True)
    amount_paid = db.Column(db.Float, nullable=False)
    change_given = db.Column(db.Float, nullable=False)
    payment_mode = db.Column(db.String(50), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items_sold = db.relationship('OfflineSaleItem', back_populates='offline_sale', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        customer = self.customer_name if self.customer_name else "Walk-in"
        return f'<Offline Sale {self.id} by {customer} - Total: {self.total_cost}>'

    def __str__(self):
        customer = self.customer_name if self.customer_name else "Walk-in"
        return f"Offline Sale {self.id} by {customer} - KSh {self.total_cost:.2f}"
    
    @property
    def items_count(self):
        return len(self.items_sold)

class OfflineSaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    offline_sale_id = db.Column(db.Integer, db.ForeignKey('offline_sale.id'), nullable=False)
    offline_sale = db.relationship('OfflineSale', back_populates='items_sold', lazy=True)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)
    variant = db.relationship('ProductVariant', backref='offline_sale_items', lazy=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_sale = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        variant_info = f"{self.variant.product.name} ({self.variant.quantity_value}{self.variant.quantity_unit})" if self.variant and self.variant.product else "N/A"
        return f'<Offline Sale Item {self.id} - {self.quantity} x {variant_info}>'

    def __str__(self):
        variant_info = f"{self.quantity} x {self.variant.product.name} ({self.variant.quantity_value}{self.variant.quantity_unit})" if self.variant and self.variant.product else "N/A"
        return f"{self.quantity} x {variant_info} @ KSh {self.price_at_sale:.2f}"

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_name = db.Column(db.String(100), nullable=False)
    author_position = db.Column(db.String(100))
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonial {self.id} by {self.author_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'author_name': self.author_name,
            'author_position': self.author_position,
            'text': self.text,
            'image_url': self.image_url,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<FAQ {self.id}: {self.question}>'

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'display_order': self.display_order
        }

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ContactMessage {self.id} from {self.name}>'

# --- ADMIN VIEWS ---
class MyAdminModelView(ModelView):
    def is_accessible(self):
        return session.get('admin_logged_in')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

class ProductAdminView(MyAdminModelView):
    column_list = ['name', 'category', 'description', 'image_url']
    column_labels = {
        'name': 'Product Name',
        'category': 'Category',
        'description': 'Description',
        'image_url': 'Image'
    }
    form_columns = ['name', 'category', 'description', 'image_url']
    column_searchable_list = ['name', 'category', 'description']
    column_filters = ['category', 'created_at']
    
    form_choices = {
        'category': [
            ('Fertilizer', 'Fertilizer'),
            ('Pesticide', 'Pesticide'),
            ('Seed', 'Seed'),
            ('Feed', 'Feed'),
            ('Other', 'Other')
        ]
    }
    
    form_args = {
        'name': {'validators': [DataRequired()]},
        'description': {'validators': [DataRequired()]},
        'category': {'validators': [DataRequired()]}
    }
    
    # Override form field creation to use SelectField for category
    def scaffold_form(self):
        form = super().scaffold_form()
        
        try:
            if hasattr(form, 'category'):
                from wtforms import SelectField
                form.category = SelectField('Category', choices=self.form_choices['category'], validators=[DataRequired()])
                print("Category field converted to SelectField successfully")
        except Exception as e:
            print(f"Error in ProductAdminView scaffold_form: {e}")
            import traceback
            traceback.print_exc()
        
        return form

class ProductVariantAdminView(MyAdminModelView):
    column_list = ['product', 'quantity_value', 'quantity_unit', 'selling_price', 'buying_price', 'stock_level', 'expiry_date', 'supplier']
    column_labels = {
        'product': 'Product',
        'quantity_value': 'Quantity',
        'quantity_unit': 'Unit',
        'selling_price': 'Selling Price',
        'buying_price': 'Buying Price',
        'stock_level': 'Stock Level',
        'expiry_date': 'Expiry Date',
        'supplier': 'Supplier'
    }
    form_columns = ['product_id', 'quantity_value', 'quantity_unit', 'selling_price', 'buying_price', 'stock_level', 'expiry_date', 'supplier']
    column_searchable_list = ['supplier']
    column_filters = ['stock_level', 'expiry_date', 'supplier']
    
    # Disable Select2Widget to avoid choice format issues
    form_widget_args = {
        'product_id': {'class': 'form-control'},
        'quantity_unit': {'class': 'form-control'}
    }
    
    def on_model_change(self, form, model, is_created):
        """Handle model changes"""
        super().on_model_change(form, model, is_created)
    

    
    form_choices = {
        'quantity_unit': [
            ('kg', 'Kilograms (kg)'),
            ('g', 'Grams (g)'),
            ('l', 'Liters (l)'),
            ('ml', 'Milliliters (ml)'),
            ('pcs', 'Pieces (pcs)'),
            ('bags', 'Bags'),
            ('bottles', 'Bottles'),
            ('cans', 'Cans'),
            ('packets', 'Packets'),
            ('boxes', 'Boxes')
        ]
    }
    
    # Ensure proper form field configuration
    def get_form(self):
        form = super().get_form()
        try:
            if hasattr(form, 'product_id'):
                form.product_id.choices = self._get_product_choices()
                print(f"Product choices set in get_form: {len(form.product_id.choices)} products")
            if hasattr(form, 'quantity_unit'):
                form.quantity_unit.choices = self.form_choices['quantity_unit']
        except Exception as e:
            print(f"Error in get_form: {e}")
            # Ensure choices are set even if there's an error
            if hasattr(form, 'product_id'):
                form.product_id.choices = []
            if hasattr(form, 'quantity_unit'):
                form.quantity_unit.choices = self.form_choices['quantity_unit']
        return form
    
    def on_form_prefill(self, form, id):
        """Ensure choices are populated when editing"""
        super().on_form_prefill(form, id)
        try:
            if hasattr(form, 'product_id'):
                form.product_id.choices = self._get_product_choices()
                print(f"Product choices populated in prefill: {len(form.product_id.choices)} products")
            if hasattr(form, 'quantity_unit'):
                form.quantity_unit.choices = self.form_choices['quantity_unit']
        except Exception as e:
            print(f"Error in on_form_prefill: {e}")
            # Ensure choices are set even if there's an error
            if hasattr(form, 'product_id'):
                form.product_id.choices = []
            if hasattr(form, 'quantity_unit'):
                form.quantity_unit.choices = self.form_choices['quantity_unit']
    
    def on_form_create(self, form):
        """Ensure choices are populated when creating"""
        super().on_form_create(form)
        try:
            if hasattr(form, 'product_id'):
                form.product_id.choices = self._get_product_choices()
                print(f"Product choices populated in create: {len(form.product_id.choices)} products")
            if hasattr(form, 'quantity_unit'):
                form.quantity_unit.choices = self.form_choices['quantity_unit']
        except Exception as e:
            print(f"Error in on_form_create: {e}")
            # Ensure choices are set even if there's an error
            if hasattr(form, 'product_id'):
                form.product_id.choices = []
            if hasattr(form, 'quantity_unit'):
                form.quantity_unit.choices = self.form_choices['quantity_unit']
    
    def _get_product_choices(self):
        """Get product choices with error handling"""
        try:
            print("_get_product_choices called - checking database...")
            # Check if database is accessible
            db.session.execute(db.text('SELECT 1'))
            print("Database connection verified")
            
            products = Product.query.order_by(Product.name).all()
            print(f"Query executed, found {len(products)} products")
            
            choices = [(p.id, p.name) for p in products]
            print(f"Successfully retrieved {len(choices)} products for choices: {choices}")
            return choices
        except Exception as e:
            print(f"Error getting product choices: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    form_args = {
        'product_id': {'validators': [DataRequired()]},
        'quantity_value': {'validators': [DataRequired()]},
        'quantity_unit': {'validators': [DataRequired()]},
        'selling_price': {'validators': [DataRequired()]},
        'stock_level': {'validators': [DataRequired()]}
    }
    
    # Override form field creation to use SelectField for product_id
    def scaffold_form(self):
        form = super().scaffold_form()
        
        try:
            if hasattr(form, 'product_id'):
                # Convert IntegerField to SelectField with choices
                from wtforms import SelectField
                # Initialize with empty choices, will be populated in on_form_prefill
                form.product_id = SelectField('Product', choices=[], validators=[DataRequired()])
                print("Product field converted to SelectField successfully")
                
                # Try to populate choices immediately
                try:
                    choices = self._get_product_choices()
                    form.product_id.choices = choices
                    print(f"Choices populated immediately in scaffold_form: {len(choices)} products")
                except Exception as e:
                    print(f"Could not populate choices immediately: {e}")
            
            # Ensure quantity_unit is properly configured as SelectField
            if hasattr(form, 'quantity_unit'):
                from wtforms import SelectField
                form.quantity_unit = SelectField('Unit', choices=self.form_choices['quantity_unit'], validators=[DataRequired()])
                print(f"Quantity unit choices: {len(self.form_choices['quantity_unit'])} units")
            
            print("Form scaffolding completed successfully")
        except Exception as e:
            print(f"Error in scaffold_form: {e}")
            import traceback
            traceback.print_exc()
            # Ensure form fields are created even if there's an error
            if hasattr(form, 'product_id'):
                from wtforms import SelectField
                form.product_id = SelectField('Product', choices=[], validators=[DataRequired()])
            if hasattr(form, 'quantity_unit'):
                from wtforms import SelectField
                form.quantity_unit = SelectField('Unit', choices=self.form_choices['quantity_unit'], validators=[DataRequired()])
        
        return form
    
    def create_form(self, obj=None):
        """Override create_form to ensure choices are populated"""
        form = super().create_form(obj)
        try:
            if hasattr(form, 'product_id'):
                form.product_id.choices = self._get_product_choices()
                print(f"Product choices populated in create_form: {len(form.product_id.choices)} products")
            if hasattr(form, 'quantity_unit'):
                form.quantity_unit.choices = self.form_choices['quantity_unit']
        except Exception as e:
            print(f"Error in create_form: {e}")
            import traceback
            traceback.print_exc()
        return form
    
    def edit_form(self, obj=None):
        """Override edit_form to ensure choices are populated"""
        form = super().edit_form(obj)
        try:
            if hasattr(form, 'product_id'):
                form.product_id.choices = self._get_product_choices()
                print(f"Product choices populated in edit_form: {len(form.product_id.choices)} products")
            if hasattr(form, 'quantity_unit'):
                form.quantity_unit.choices = self.form_choices['quantity_unit']
        except Exception as e:
            print(f"Error in edit_form: {e}")
            import traceback
            traceback.print_exc()
        return form
    
    create_modal = False
    edit_modal = False

class OrderAdminView(MyAdminModelView):
    column_list = ['customer_name', 'customer_email', 'customer_phone', 'total_amount', 'ordered_at', 'payment_status']
    column_labels = {
        'customer_name': 'Customer Name',
        'customer_email': 'Email',
        'customer_phone': 'Phone',
        'total_amount': 'Total Amount',
        'ordered_at': 'Order Date',
        'payment_status': 'Payment Status'
    }
    form_columns = ['customer_name', 'customer_email', 'customer_phone', 'delivery_address', 'total_amount', 'payment_status']
    column_searchable_list = ['customer_name', 'customer_email', 'customer_phone']
    column_filters = ['payment_status', 'ordered_at']
    
    form_args = {
        'customer_name': {'validators': [DataRequired()]},
        'customer_email': {'validators': [DataRequired(), Email()]},
        'customer_phone': {'validators': [DataRequired()]},
        'delivery_address': {'validators': [DataRequired()]}
    }
    
    form_choices = {
        'payment_status': [
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Cancelled', 'Cancelled'),
            ('Refunded', 'Refunded')
        ]
    }
    
    form_widget_args = {
        'total_amount': {'readonly': True}
    }
    
    # Ensure proper form field configuration
    def get_form(self):
        form = super().get_form()
        try:
            if hasattr(form, 'order_id'):
                form.order_id.choices = self._get_order_choices()
            if hasattr(form, 'product_variant_id'):
                form.product_variant_id.choices = self._get_variant_choices()
        except Exception as e:
            print(f"Error in OrderAdminView get_form: {e}")
            # Ensure choices are set even if there's an error
            if hasattr(form, 'order_id'):
                form.order_id.choices = []
            if hasattr(form, 'product_variant_id'):
                form.product_variant_id.choices = []
        return form
    
    def _get_order_choices(self):
        """Get order choices with error handling"""
        try:
            # Check if database is accessible
            db.session.execute(db.text('SELECT 1'))
            orders = Order.query.order_by(Order.id.desc()).all()
            return [(o.id, f"Order {o.id} - {o.customer_name}") for o in orders]
        except Exception as e:
            print(f"Error getting order choices: {e}")
            return []
    
    def _get_variant_choices(self):
        """Get variant choices with error handling"""
        try:
            # Check if database is accessible
            db.session.execute(db.text('SELECT 1'))
            variants = ProductVariant.query.join(Product).order_by(Product.name, ProductVariant.quantity_value).all()
            return [(v.id, f"{v.product.name} - {v.quantity_value}{v.quantity_unit}") for v in variants]
        except Exception as e:
            print(f"Error getting variant choices: {e}")
            return []
    
    def on_form_prefill(self, form, id):
        """Ensure choices are populated when editing"""
        super().on_form_prefill(form, id)
        try:
            if hasattr(form, 'order_id'):
                form.order_id.choices = self._get_order_choices()
            if hasattr(form, 'product_variant_id'):
                form.product_variant_id.choices = self._get_variant_choices()
        except Exception as e:
            print(f"Error in OrderItem on_form_prefill: {e}")
            # Ensure choices are set even if there's an error
            if hasattr(form, 'order_id'):
                form.order_id.choices = []
            if hasattr(form, 'product_variant_id'):
                form.product_variant_id.choices = []
    
    def on_form_create(self, form):
        """Ensure choices are populated when creating"""
        super().on_form_create(form)
        try:
            if hasattr(form, 'order_id'):
                form.order_id.choices = self._get_order_choices()
            if hasattr(form, 'product_variant_id'):
                form.product_variant_id.choices = self._get_variant_choices()
        except Exception as e:
            print(f"Error in OrderItem on_form_create: {e}")
            # Ensure choices are set even if there's an error
            if hasattr(form, 'order_id'):
                form.order_id.choices = []
            if hasattr(form, 'product_variant_id'):
                form.product_variant_id.choices = []
    
    create_modal = False
    edit_modal = False

class OrderItemAdminView(MyAdminModelView):
    column_list = ['order', 'variant', 'quantity', 'price_at_purchase']
    column_labels = {
        'order': 'Parent Order',
        'variant': 'Product Variant',
        'quantity': 'Quantity',
        'price_at_purchase': 'Price at Purchase'
    }
    form_columns = ['order_id', 'product_variant_id', 'quantity', 'price_at_purchase']
    
    form_args = {
        'order_id': {'validators': [DataRequired()]},
        'product_variant_id': {'validators': [DataRequired()]},
        'quantity': {'validators': [DataRequired()]},
        'price_at_purchase': {'validators': [DataRequired()]}
    }
    
    # Disable Select2Widget to avoid choice format issues
    form_widget_args = {
        'order_id': {'class': 'form-control'},
        'product_variant_id': {'class': 'form-control'}
    }
    
    # Override form field creation to use SelectField for foreign keys
    def scaffold_form(self):
        form = super().scaffold_form()
        
        try:
            if hasattr(form, 'order_id'):
                # Convert IntegerField to SelectField with choices
                from wtforms import SelectField
                # Populate choices immediately to avoid rendering issues
                try:
                    # Check if database is accessible
                    db.session.execute(db.text('SELECT 1'))
                    orders = Order.query.order_by(Order.id.desc()).all()
                    choices = [(o.id, f"Order {o.id} - {o.customer_name}") for o in orders]
                    print(f"Order choices populated: {len(choices)} orders")
                except Exception as e:
                    print(f"Error populating order choices: {e}")
                    choices = []
                form.order_id = SelectField('Order', choices=choices, validators=[DataRequired()])
            
            if hasattr(form, 'product_variant_id'):
                # Convert IntegerField to SelectField with choices
                from wtforms import SelectField
                # Populate choices immediately to avoid rendering issues
                try:
                    # Check if database is accessible
                    db.session.execute(db.text('SELECT 1'))
                    variants = ProductVariant.query.join(Product).order_by(Product.name, ProductVariant.quantity_value).all()
                    choices = [(v.id, f"{v.product.name} - {v.quantity_value}{v.quantity_unit}") for v in variants]
                    print(f"Variant choices populated: {len(choices)} variants")
                except Exception as e:
                    print(f"Error populating variant choices: {e}")
                    choices = []
                form.product_variant_id = SelectField('Product Variant', choices=choices, validators=[DataRequired()])
            
            print("OrderItem form scaffolding completed successfully")
        except Exception as e:
            print(f"Error in OrderItem scaffold_form: {e}")
            import traceback
            traceback.print_exc()
            # Ensure form fields are created even if there's an error
            if hasattr(form, 'order_id'):
                from wtforms import SelectField
                form.order_id = SelectField('Order', choices=[], validators=[DataRequired()])
            if hasattr(form, 'product_variant_id'):
                from wtforms import SelectField
                form.product_variant_id = SelectField('Product Variant', choices=[], validators=[DataRequired()])
        
        return form
    
    def on_form_prefill(self, form, id):
        """Populate choices when editing"""
        if hasattr(form, 'order_id') and hasattr(form.order_id, 'choices'):
            try:
                orders = Order.query.order_by(Order.id.desc()).all()
                form.order_id.choices = [(o.id, f"Order {o.id} - {o.customer_name}") for o in orders]
            except Exception as e:
                print(f"Error populating order choices: {e}")
                form.order_id.choices = []
        if hasattr(form, 'product_variant_id') and hasattr(form.product_variant_id, 'choices'):
            try:
                variants = ProductVariant.query.all()
                form.product_variant_id.choices = [(v.id, f"{v.product.name} ({v.quantity_value}{v.quantity_unit})") for v in variants if v.product]
            except Exception as e:
                print(f"Error populating variant choices: {e}")
                form.product_variant_id.choices = []
        super().on_form_prefill(form, id)
    
    def on_form_create(self, form):
        """Populate choices when creating new record"""
        if hasattr(form, 'order_id') and hasattr(form.order_id, 'choices'):
            try:
                orders = Order.query.order_by(Order.id.desc()).all()
                form.order_id.choices = [(o.id, f"Order {o.id} - {o.customer_name}") for o in orders]
            except Exception as e:
                print(f"Error populating order choices: {e}")
                form.order_id.choices = []
        if hasattr(form, 'product_variant_id') and hasattr(form.product_variant_id, 'choices'):
            try:
                variants = ProductVariant.query.all()
                form.product_variant_id.choices = [(v.id, f"{v.product.name} ({v.quantity_value}{v.quantity_unit})") for v in variants if v.product]
            except Exception as e:
                print(f"Error populating variant choices: {e}")
                form.product_variant_id.choices = []
        super().on_form_create(form)
    
    create_modal = False
    edit_modal = False

class OfflineSaleAdminView(MyAdminModelView):
    column_list = ['customer_name', 'total_cost', 'amount_paid', 'change_given', 'payment_mode', 'sale_date']
    column_labels = {
        'customer_name': 'Customer Name',
        'total_cost': 'Total Cost',
        'amount_paid': 'Amount Paid',
        'change_given': 'Change Given',
        'payment_mode': 'Payment Mode',
        'sale_date': 'Sale Date'
    }
    form_columns = ['customer_name', 'total_cost', 'amount_paid', 'change_given', 'payment_mode']
    column_searchable_list = ['customer_name', 'payment_mode']
    column_filters = ['payment_mode', 'sale_date']
    
    form_choices = {
        'payment_mode': [
            ('Cash', 'Cash'),
            ('M-Pesa', 'M-Pesa'),
            ('Card', 'Card'),
            ('Bank Transfer', 'Bank Transfer')
        ]
    }
    
    form_args = {
        'total_cost': {'validators': [DataRequired()]},
        'amount_paid': {'validators': [DataRequired()]},
        'change_given': {'validators': [DataRequired()]},
        'payment_mode': {'validators': [DataRequired()]}
    }
    
    create_modal = False
    edit_modal = False

class OfflineSaleItemAdminView(MyAdminModelView):
    column_list = ['offline_sale', 'variant', 'quantity', 'price_at_sale']
    column_labels = {
        'offline_sale': 'Parent Sale',
        'variant': 'Product Variant',
        'quantity': 'Quantity',
        'price_at_sale': 'Price at Sale'
    }
    form_columns = ['offline_sale_id', 'product_variant_id', 'quantity', 'price_at_sale']
    
    form_args = {
        'offline_sale_id': {'validators': [DataRequired()]},
        'product_variant_id': {'validators': [DataRequired()]},
        'quantity': {'validators': [DataRequired()]},
        'price_at_sale': {'validators': [DataRequired()]}
    }
    
    # Override form field creation to use SelectField for foreign keys
    def scaffold_form(self):
        form = super().scaffold_form()
        if hasattr(form, 'offline_sale_id'):
            # Convert IntegerField to SelectField with choices
            from wtforms import SelectField
            # Initialize with empty choices, will be populated in on_form_prefill
            form.offline_sale_id = SelectField('Offline Sale', choices=[], validators=[DataRequired()])
        if hasattr(form, 'product_variant_id'):
            # Convert IntegerField to SelectField with choices
            from wtforms import SelectField
            # Initialize with empty choices, will be populated in on_form_prefill
            form.product_variant_id = SelectField('Product Variant', choices=[], validators=[DataRequired()])
        return form
    
    def on_form_prefill(self, form, id):
        """Populate choices when editing"""
        if hasattr(form, 'offline_sale_id') and hasattr(form.offline_sale_id, 'choices'):
            try:
                sales = OfflineSale.query.order_by(OfflineSale.id.desc()).all()
                form.offline_sale_id.choices = [(s.id, f"Sale {s.id} - {s.customer_name or 'Walk-in'}") for s in sales]
            except Exception as e:
                print(f"Error populating sale choices: {e}")
                form.offline_sale_id.choices = []
        if hasattr(form, 'product_variant_id') and hasattr(form.product_variant_id, 'choices'):
            try:
                variants = ProductVariant.query.all()
                form.product_variant_id.choices = [(v.id, f"{v.product.name} ({v.quantity_value}{v.quantity_unit})") for v in variants if v.product]
            except Exception as e:
                print(f"Error populating variant choices: {e}")
                form.product_variant_id.choices = []
        super().on_form_prefill(form, id)
    
    def on_form_create(self, form):
        """Populate choices when creating new record"""
        if hasattr(form, 'offline_sale_id') and hasattr(form.offline_sale_id, 'choices'):
            try:
                sales = OfflineSale.query.order_by(OfflineSale.id.desc()).all()
                form.offline_sale_id.choices = [(s.id, f"Sale {s.id} - {s.customer_name or 'Walk-in'}") for s in sales]
            except Exception as e:
                print(f"Error populating sale choices: {e}")
                form.offline_sale_id.choices = []
        if hasattr(form, 'product_variant_id') and hasattr(form.product_variant_id, 'choices'):
            try:
                variants = ProductVariant.query.all()
                form.product_variant_id.choices = [(v.id, f"{v.product.name} ({v.quantity_value}{v.quantity_unit})") for v in variants if v.product]
            except Exception as e:
                print(f"Error populating variant choices: {e}")
                form.product_variant_id.choices = []
        super().on_form_create(form)
    
    create_modal = False
    edit_modal = False

class TestimonialAdminView(MyAdminModelView):
    column_list = ['author_name', 'author_position', 'text', 'is_approved', 'created_at']
    column_labels = {
        'author_name': 'Author Name',
        'author_position': 'Position',
        'text': 'Testimonial Text',
        'is_approved': 'Approved',
        'created_at': 'Created At'
    }
    form_columns = ['author_name', 'author_position', 'text', 'image_url', 'is_approved']
    column_searchable_list = ['author_name', 'text']
    column_filters = ['is_approved', 'created_at']
    
    form_choices = {
        'is_approved': [
            (True, 'Yes'),
            (False, 'No')
        ]
    }
    
    form_args = {
        'author_name': {'validators': [DataRequired()]},
        'text': {'validators': [DataRequired()]}
    }
    
    create_modal = False
    edit_modal = False

class FAQAdminView(MyAdminModelView):
    column_list = ['question', 'answer', 'display_order', 'id']
    column_labels = {
        'question': 'Question',
        'answer': 'Answer',
        'display_order': 'Display Order',
        'id': 'ID'
    }
    form_columns = ['question', 'answer', 'display_order']
    column_searchable_list = ['question', 'answer']
    column_filters = ['display_order']
    
    form_args = {
        'question': {'validators': [DataRequired()]},
        'answer': {'validators': [DataRequired()]}
    }
    
    create_modal = False
    edit_modal = False

class ContactMessageAdminView(MyAdminModelView):
    column_list = ['name', 'email', 'phone', 'subject', 'is_read', 'submitted_at']
    column_labels = {
        'name': 'Name',
        'email': 'Email',
        'phone': 'Phone',
        'subject': 'Subject',
        'is_read': 'Read',
        'submitted_at': 'Submitted At'
    }
    form_columns = ['name', 'email', 'phone', 'subject', 'message', 'is_read']
    column_searchable_list = ['name', 'email', 'subject', 'message']
    column_filters = ['is_read', 'submitted_at']
    can_create = False  # Contact messages are submitted by users
    can_delete = True
    
    form_choices = {
        'is_read': [
            (True, 'Yes'),
            (False, 'No')
        ]
    }
    
    form_args = {
        'name': {'validators': [DataRequired()]},
        'email': {'validators': [DataRequired(), Email()]},
        'message': {'validators': [DataRequired()]}
    }
    
    create_modal = False
    edit_modal = False

class ManualSaleView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/manual_sale.html')

class DashboardView(BaseView):
    @expose('/')
    def index(self):
        return redirect(url_for('admin_dashboard'))

# --- ADMIN SETUP ---
def setup_admin():
    """Setup admin views within application context"""
    admin = Admin(app, name='Kaboy Agrovet Admin', template_mode='bootstrap3')
    
    # Add admin views
    admin.add_view(OrderAdminView(Order, db.session, name='Customer Orders'))
    admin.add_view(ProductAdminView(Product, db.session, name='Products'))
    admin.add_view(ProductVariantAdminView(ProductVariant, db.session, name='Product Variants'))
    admin.add_view(TestimonialAdminView(Testimonial, db.session, name='Testimonials'))
    admin.add_view(FAQAdminView(FAQ, db.session, name='FAQs'))
    admin.add_view(ContactMessageAdminView(ContactMessage, db.session, name='Contact Messages'))
    admin.add_view(OrderItemAdminView(OrderItem, db.session, name='Order Items'))
    admin.add_view(OfflineSaleAdminView(OfflineSale, db.session, name='Offline Sales'))
    admin.add_view(OfflineSaleItemAdminView(OfflineSaleItem, db.session, name='Offline Sale Items'))
    admin.add_view(ManualSaleView(name='Manual Sales', endpoint='manual_sale'))
    admin.add_view(DashboardView(name='Dashboard', endpoint='dashboard'))
    
    return admin

# Initialize admin later in the app context
admin = None

# --- API ROUTES FOR MANUAL SALES ---
@app.route('/api/products')
def get_products():
    search = request.args.get('search', '')
    products_query = Product.query
    
    if search:
        products_query = products_query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )
    
    products = products_query.order_by(Product.name).all()
    
    result = []
    for product in products:
        product_data = product.to_dict()
        # Add variants with more details
        variants_data = []
        for variant in product.variants:
            variant_data = variant.to_dict()
            variant_data['display_name'] = f"{product.name} ({variant.quantity_value}{variant.quantity_unit})"
            variants_data.append(variant_data)
        product_data['variants'] = variants_data
        result.append(product_data)
    
    return jsonify(result)

@app.route('/api/product-variants')
def get_product_variants():
    search = request.args.get('search', '')
    variants_query = ProductVariant.query.join(Product)
    
    if search:
        variants_query = variants_query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                ProductVariant.quantity_unit.ilike(f'%{search}%'),
                ProductVariant.supplier.ilike(f'%{search}%')
            )
        )
    
    variants = variants_query.all()
    
    result = []
    for variant in variants:
        variant_data = variant.to_dict()
        variant_data['display_name'] = f"{variant.product.name} ({variant.quantity_value}{variant.quantity_unit}) - KSh {variant.selling_price}"
        result.append(variant_data)
    
    return jsonify(result)

@app.route('/api/testimonials')
def get_testimonials():
    try:
        testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
        return jsonify([{
            'id': testimonial.id,
            'author_name': testimonial.author_name,
            'author_position': testimonial.author_position,
            'text': testimonial.text,
            'image_url': testimonial.image_url,
            'created_at': testimonial.created_at.isoformat() if testimonial.created_at else None
        } for testimonial in testimonials])
    except Exception as e:
        print(f"Error in get_testimonials: {e}")
        return jsonify({
            'error': 'Failed to load testimonials',
            'message': str(e)
        }), 500

@app.route('/api/faqs')
def get_faqs():
    try:
        faqs = FAQ.query.order_by(FAQ.display_order, FAQ.id).all()
        return jsonify([{
            'id': faq.id,
            'question': faq.question,
            'answer': faq.answer,
            'display_order': faq.display_order
        } for faq in faqs])
    except Exception as e:
        print(f"Error in get_faqs: {e}")
        return jsonify({
            'error': 'Failed to load FAQs',
            'message': str(e)
        }), 500

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400
        
        # Create contact message
        contact_msg = ContactMessage(
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            subject=data.get('subject', 'General Inquiry'),
            message=data.get('message', '')
        )
        db.session.add(contact_msg)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contact message received successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing contact form: {str(e)}'
        }), 500

@app.route('/api/submit-full-order', methods=['POST'])
def submit_full_order():
    """Submit a full order from the cart"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400
        
        # Extract order details
        customer_name = data.get('customer_name', '')
        customer_email = data.get('customer_email', '')
        customer_phone = data.get('customer_phone', '')
        delivery_address = data.get('delivery_address', '')
        cart_items = data.get('items', [])
        
        # Debug logging
        print(f"DEBUG: Received cart items: {cart_items}")
        print(f"DEBUG: Cart items types: {[(type(item.get('selling_price')), type(item.get('quantity'))) for item in cart_items]}")
        
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
        
        # Validate cart items structure and data types
        for i, item in enumerate(cart_items):
            if 'product_variant_id' not in item:
                return jsonify({
                    'success': False, 
                    'message': f'Missing product_variant_id in item {i+1}'
                }), 400
            if 'quantity' not in item:
                return jsonify({
                    'success': False, 
                    'message': f'Missing quantity in item {i+1}'
                }), 400
            if 'selling_price' not in item:
                return jsonify({
                    'success': False, 
                    'message': f'Missing selling_price in item {i+1}. Available fields: {list(item.keys())}'
                }), 400
            
            # Validate data types
            try:
                int(item['quantity'])
                float(item['selling_price'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': f'Invalid data types in item {i+1}. quantity must be a number, selling_price must be a number. Received: quantity={item["quantity"]} ({type(item["quantity"])}), selling_price={item["selling_price"]} ({type(item["selling_price"])})'
                }), 400
        
        # Calculate total amount with proper type conversion
        total_amount = 0
        for item in cart_items:
            try:
                selling_price = float(item['selling_price'])
                quantity = int(item['quantity'])
                total_amount += selling_price * quantity
            except (ValueError, TypeError) as e:
                return jsonify({
                    'success': False,
                    'message': f'Invalid data type in item {cart_items.index(item)+1}. selling_price: {item.get("selling_price")} ({type(item.get("selling_price"))}), quantity: {item.get("quantity")} ({type(item.get("quantity"))})'
                }), 400
        
        # Create the order
        order = Order(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            delivery_address=delivery_address,
            total_amount=total_amount
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_variant_id=item['product_variant_id'],
                quantity=item['quantity'],
                price_at_purchase=item['selling_price']
            )
            db.session.add(order_item)
            
            # Update stock level
            variant = ProductVariant.query.get(item['product_variant_id'])
            if variant:
                variant.stock_level = max(0, variant.stock_level - item['quantity'])
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Order submitted successfully! Order ID: {order.id}',
            'order_id': order.id
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error in submit_full_order: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error submitting order: {str(e)}'
        }), 500

@app.route('/api/manual-sale', methods=['POST'])
def submit_manual_sale():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data received'
            }), 400
        
        # Validate required fields
        required_fields = ['total_cost', 'amount_paid', 'payment_mode', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        if not data['items'] or len(data['items']) == 0:
            return jsonify({
                'success': False,
                'message': 'No items in sale'
            }), 400
        
        # Create offline sale
        sale = OfflineSale(
            customer_name=data.get('customer_name', ''),
            total_cost=float(data['total_cost']),
            amount_paid=float(data['amount_paid']),
            change_given=float(data['change_given']),
            payment_mode=data['payment_mode']
        )
        db.session.add(sale)
        db.session.flush()  # Get the sale ID
        
        # Add sale items
        for item_data in data['items']:
            if 'product_variant_id' not in item_data:
                return jsonify({
                    'success': False,
                    'message': 'Missing product_variant_id in item'
                }), 400
                
            variant_id = item_data['product_variant_id']
            quantity = int(item_data['quantity'])
            price = float(item_data['price'])
            
            # Verify product variant exists
            variant = ProductVariant.query.get(variant_id)
            if not variant:
                return jsonify({
                    'success': False,
                    'message': f'Product variant with ID {variant_id} not found'
                }), 400
            
            sale_item = OfflineSaleItem(
                offline_sale_id=sale.id,
                product_variant_id=variant_id,
                quantity=quantity,
                price_at_sale=price
            )
            db.session.add(sale_item)
            
            # Update stock level
            variant.stock_level = max(0, variant.stock_level - quantity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sale recorded successfully!',
            'sale_id': sale.id
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error in manual sale: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error recording sale: {str(e)}'
        }), 500

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple admin login (you can enhance this)
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin-dashboard/')
def admin_dashboard():
    """Custom admin dashboard with charts and analytics"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin-orders/')
def admin_orders():
    """Unified orders view showing both online and offline sales"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_orders.html')

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Get dashboard analytics data"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get current date and last month date
        now = datetime.utcnow()
        last_month = now - timedelta(days=30)
        
        # Calculate statistics
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        total_orders = Order.query.count()
        total_products = Product.query.count()
        total_customers = db.session.query(db.func.count(db.func.distinct(Order.customer_email))).scalar() or 0
        
        # Calculate revenue change (simplified - you can enhance this)
        last_month_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.ordered_at >= last_month
        ).scalar() or 0
        
        revenue_change = 0
        if last_month_revenue > 0:
            revenue_change = ((total_revenue - last_month_revenue) / last_month_revenue) * 100
        
        # Get revenue trend for last 7 days
        revenue_trend = []
        for i in range(7):
            date = now - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            daily_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
                Order.ordered_at >= day_start,
                Order.ordered_at < day_end
            ).scalar() or 0
            
            revenue_trend.insert(0, {
                'date': date.strftime('%a'),
                'revenue': daily_revenue
            })
        
        # Get top products by sales
        try:
            top_products = db.session.query(
                Product.name,
                db.func.count(OrderItem.id).label('sales')
            ).select_from(Product).join(ProductVariant, Product.id == ProductVariant.product_id).join(OrderItem, ProductVariant.id == OrderItem.product_variant_id).group_by(Product.id).order_by(
                db.func.count(OrderItem.id).desc()
            ).limit(5).all()
            
            top_products_data = []
            for name, sales in top_products:
                try:
                    top_products_data.append({
                        'name': str(name) if name else 'Unknown Product',
                        'sales': int(sales) if sales else 0
                    })
                except Exception as e:
                    print(f"Error processing product data: {e}")
                    continue
        except Exception as e:
            print(f"Error getting top products: {e}")
            top_products_data = []
        
        # Get recent activities
        recent_orders = Order.query.order_by(Order.ordered_at.desc()).limit(4).all()
        recent_activities = []
        
        for order in recent_orders:
            recent_activities.append({
                'type': 'order',
                'title': f'Order #{order.id} Received',
                'description': f'{order.customer_name} - KSh {order.total_amount:,.0f}',
                'timestamp': order.ordered_at.isoformat()
            })
        
        # Add some sample activities if not enough orders
        if len(recent_activities) < 4:
            recent_activities.append({
                'type': 'sale',
                'title': 'Manual Sale Recorded',
                'description': 'Walk-in customer - KSh 2,500',
                'timestamp': (now - timedelta(hours=2)).isoformat()
            })
        
        # Get low stock alerts
        low_stock_threshold = 10  # Alert when stock is 10 or below
        low_stock_alerts = db.session.query(
            ProductVariant.id,
            Product.name.label('product_name'),
            ProductVariant.quantity_value,
            ProductVariant.quantity_unit,
            ProductVariant.stock_level
        ).join(Product).filter(
            ProductVariant.stock_level <= low_stock_threshold
        ).order_by(ProductVariant.stock_level.asc()).limit(10).all()
        
        low_stock_data = []
        for alert in low_stock_alerts:
            low_stock_data.append({
                'id': alert.id,
                'product_name': alert.product_name,
                'quantity_value': alert.quantity_value,
                'quantity_unit': alert.quantity_unit,
                'stock_level': alert.stock_level
            })
        
        return jsonify({
            'stats': {
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'total_products': total_products,
                'total_customers': total_customers,
                'revenue_change': round(revenue_change, 1),
                'orders_change': 8.3,  # Placeholder
                'products_change': 5.2,  # Placeholder
                'customers_change': 15.7  # Placeholder
            },
            'revenue_trend': revenue_trend,
            'top_products': top_products_data,
            'recent_activities': recent_activities[:4],
            'low_stock_alerts': low_stock_data
        })
        
    except Exception as e:
        print(f"Error getting dashboard data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to load dashboard data'}), 500

@app.route('/api/all-orders')
def get_all_orders():
    """Get all orders (online + offline) for the orders dashboard"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get online orders
        online_orders = db.session.query(
            Order.id,
            Order.customer_name,
            Order.customer_email,
            Order.customer_phone,
            Order.total_amount,
            Order.ordered_at,
            Order.payment_status,
            db.literal('online').label('order_type')
        ).order_by(Order.ordered_at.desc()).all()
        
        # Get offline sales
        offline_sales = db.session.query(
            OfflineSale.id,
            OfflineSale.customer_name,
            db.literal('').label('customer_email'),
            db.literal('').label('customer_phone'),
            OfflineSale.total_cost,
            OfflineSale.sale_date,
            OfflineSale.payment_mode,
            db.literal('offline').label('order_type')
        ).order_by(OfflineSale.sale_date.desc()).all()
        
        # Combine and format data
        all_orders = []
        
        for order in online_orders:
            all_orders.append({
                'id': order.id,
                'customer_name': order.customer_name or 'N/A',
                'customer_email': order.customer_email or 'N/A',
                'customer_phone': order.customer_phone or 'N/A',
                'total_amount': order.total_amount,
                'date': order.ordered_at,
                'payment_info': order.payment_status,
                'order_type': order.order_type,
                'status_color': 'success' if order.payment_status == 'Paid' else 'warning' if order.payment_status == 'Pending' else 'danger'
            })
        
        for sale in offline_sales:
            all_orders.append({
                'id': sale.id,
                'customer_name': sale.customer_name or 'Walk-in Customer',
                'customer_email': 'N/A',
                'customer_phone': 'N/A',
                'total_amount': sale.total_cost,
                'date': sale.sale_date,
                'payment_info': sale.payment_mode,
                'order_type': sale.order_type,
                'status_color': 'success'  # Offline sales are always completed
            })
        
        # Sort by date (newest first)
        all_orders.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'orders': all_orders,
            'total_count': len(all_orders),
            'online_count': len(online_orders),
            'offline_count': len(offline_sales)
        })
        
    except Exception as e:
        print(f"Error getting all orders: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to load orders data'}), 500

def create_default_admin():
    """Create default admin user if none exists"""
    try:
        print("Default admin credentials: username='admin', password='admin123'")
        print("IMPORTANT: Change the default password after first login!")
    except Exception as e:
        print(f"Error setting up admin: {e}")

def create_sample_data():
    """Create sample data for testing"""
    try:
        # Check if we already have products
        if Product.query.first():
            print("Sample data already exists")
            return
        
        # Create sample products
        product1 = Product(name="NPK Fertilizer", category="Fertilizer", description="Complete fertilizer for all crops")
        product2 = Product(name="DAP Fertilizer", category="Fertilizer", description="Phosphate fertilizer for root development")
        product3 = Product(name="Seeds Mix", category="Seed", description="Mixed vegetable seeds")
        product4 = Product(name="Pesticide", category="Pesticide", description="General purpose pesticide")
        
        db.session.add_all([product1, product2, product3, product4])
        db.session.commit()
        
        # Create sample variants
        variant1 = ProductVariant(
            product_id=product1.id,
            quantity_value=50.0,
            quantity_unit="kg",
            selling_price=2500.0,
            buying_price=2000.0,
            stock_level=20,
            supplier="Kenya Seed Co."
        )
        variant2 = ProductVariant(
            product_id=product1.id,
            quantity_value=25.0,
            quantity_unit="kg",
            selling_price=1300.0,
            buying_price=1100.0,
            stock_level=15,
            supplier="Kenya Seed Co."
        )
        variant3 = ProductVariant(
            product_id=product2.id,
            quantity_value=50.0,
            quantity_unit="kg",
            selling_price=2800.0,
            buying_price=2300.0,
            stock_level=12,
            supplier="Kenya Seed Co."
        )
        variant4 = ProductVariant(
            product_id=product3.id,
            quantity_value=100.0,
            quantity_unit="g",
            selling_price=150.0,
            buying_price=100.0,
            stock_level=50,
            supplier="Local Supplier"
        )
        variant5 = ProductVariant(
            product_id=product4.id,
            quantity_value=1.0,
            quantity_unit="L",
            selling_price=800.0,
            buying_price=600.0,
            stock_level=30,
            supplier="AgroChem Ltd"
        )
        
        db.session.add_all([variant1, variant2, variant3, variant4, variant5])
        db.session.commit()
        
        print("✅ Sample data created successfully!")
        print("📦 Products created: NPK Fertilizer, DAP Fertilizer, Seeds Mix, Pesticide")
        print("🔧 Variants created with different quantities and prices")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        try:
            print("Initializing database...")
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"Current working directory: {os.getcwd()}")
            
            # Check if database file exists
            db_path = 'kaboy_agrovet.db'
            if os.path.exists(db_path):
                print(f"Database file already exists: {db_path}")
            else:
                print(f"Database file will be created at: {db_path}")
            
            db.create_all()
            print("Database tables created successfully")
            
            # Verify database connection
            try:
                db.session.execute(db.text('SELECT 1'))
                print("Database connection verified successfully")
            except Exception as e:
                print(f"Database connection verification failed: {e}")
                raise
            
            print("Setting up admin...")
            create_default_admin()
            
            # Setup admin views within app context
            admin = setup_admin()
            print("Admin views configured successfully")
            
            print("Creating sample data...")
            create_sample_data()
            
            print("✅ Application initialization completed successfully!")
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            import traceback
            traceback.print_exc()
    
    print("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000) 