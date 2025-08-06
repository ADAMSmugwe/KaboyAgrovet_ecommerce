# app_simple_admin.py - Simplified Flask Admin Version
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from wtforms import FloatField, StringField, HiddenField, SelectField, IntegerField, DateTimeField, PasswordField
from wtforms.widgets import TextInput
from flask_admin import expose
from wtforms.widgets import Select
from flask_admin.form.widgets import Select2Widget
from flask_mail import Mail, Message
from wtforms.validators import DataRequired, Email, Length, EqualTo
import secrets
import string

load_dotenv()

app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'))
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(app.instance_path, 'kaboy_agrovet.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['FLASK_ADMIN_SWATCH'] = 'yeti'

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Simple Flask Admin setup
admin = Admin(app, name='Kaboy Agrovet Admin', template_mode='bootstrap3')

# --- MODEL DEFINITIONS ---
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(50), default='Pending', nullable=False)
    items = db.relationship('OrderItem', back_populates='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id} by {self.customer_name} - Total: {self.total_amount}>'

    def __str__(self):
        return f'Order {self.id} by {self.customer_name}'
    
    @property
    def items_count(self):
        return len(self.items)

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

    def __repr__(self):
        product_name = self.product.name if self.product else "N/A"
        return f'<Variant {self.quantity_value}{self.quantity_unit} of {product_name} (Stock: {self.stock_level})>'

    def to_dict(self):
        return {
            'id': self.id,
            'quantity_value': self.quantity_value,
            'quantity_unit': self.quantity_unit,
            'selling_price': self.selling_price,
            'stock_level': self.stock_level,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'supplier': self.supplier
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order = db.relationship('Order', back_populates='items', lazy=True)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)
    variant = db.relationship('ProductVariant', backref='order_items', lazy=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

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
    items_sold = db.relationship('OfflineSaleItem', back_populates='offline_sale', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<OfflineSale {self.id} - {self.customer_name or "Walk-in"} - KSh {self.total_cost}>'

    def __str__(self):
        return f"Sale {self.id} - {self.customer_name or 'Walk-in'} - KSh {self.total_cost}"
    
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

    def __repr__(self):
        variant_info = f"{self.variant.product.name} ({self.variant.quantity_value}{self.variant.quantity_unit})" if self.variant and self.variant.product else "N/A"
        return f'<OfflineSaleItem {self.id} - {self.quantity} x {variant_info}>'

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

# --- SIMPLE ADMIN VIEWS ---
class SimpleModelView(ModelView):
    def is_accessible(self):
        return True  # No authentication for now
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

# Add simple admin views
admin.add_view(SimpleModelView(Order, db.session, name='Orders'))
admin.add_view(SimpleModelView(Product, db.session, name='Products'))
admin.add_view(SimpleModelView(ProductVariant, db.session, name='Product Variants'))
admin.add_view(SimpleModelView(OrderItem, db.session, name='Order Items'))
admin.add_view(SimpleModelView(OfflineSale, db.session, name='Offline Sales'))
admin.add_view(SimpleModelView(OfflineSaleItem, db.session, name='Offline Sale Items'))
admin.add_view(SimpleModelView(Testimonial, db.session, name='Testimonials'))
admin.add_view(SimpleModelView(FAQ, db.session, name='FAQs'))
admin.add_view(SimpleModelView(ContactMessage, db.session, name='Contact Messages'))

# --- BASIC ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/products')
def get_products():
    search_term = request.args.get('search')

    products_query = Product.query

    if search_term:
        products_query = products_query.filter(
            (Product.name.ilike(f'%{search_term}%')) |
            (Product.description.ilike(f'%{search_term}%'))
        )

    products = products_query.order_by(Product.name).all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/product-variants')
def get_product_variants():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = ProductVariant.query.join(Product)
    
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%'),
                ProductVariant.supplier.ilike(f'%{search}%')
            )
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    # Only return variants with stock > 0
    query = query.filter(ProductVariant.stock_level > 0)
    
    variants = query.all()
    
    result = []
    for variant in variants:
        variant_data = variant.to_dict()
        variant_data['product_name'] = variant.product.name
        variant_data['product_category'] = variant.product.category
        variant_data['product_description'] = variant.product.description
        variant_data['product_image_url'] = variant.product.image_url
        result.append(variant_data)
    
    return jsonify(result)

@app.route('/api/testimonials')
def get_testimonials():
    testimonials = Testimonial.query.filter_by(is_approved=True).all()
    return jsonify([t.to_dict() for t in testimonials])

@app.route('/api/faqs')
def get_faqs():
    faqs = FAQ.query.order_by(FAQ.display_order).all()
    return jsonify([f.to_dict() for f in faqs])

@app.route('/api/contact', methods=['POST'])
def submit_contact_message():
    try:
        data = request.get_json()
        
        message = ContactMessage(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            subject=data.get('subject', 'Contact Form Submission'),
            message=data['message']
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Message sent successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/submit-full-order', methods=['POST'])
def submit_full_order():
    try:
        data = request.get_json()
        
        # Create order
        order = Order(
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            delivery_address=data['delivery_address'],
            total_amount=data['total_amount'],
            payment_status='Pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items
        for item_data in data['items']:
            order_item = OrderItem(
                order_id=order.id,
                product_variant_id=item_data['variant_id'],
                quantity=item_data['quantity'],
                price_at_purchase=item_data['price']
            )
            db.session.add(order_item)
            
            # Update stock level
            variant = ProductVariant.query.get(item_data['variant_id'])
            if variant:
                variant.stock_level -= item_data['quantity']
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Order submitted successfully!', 'order_id': order.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple admin authentication
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 