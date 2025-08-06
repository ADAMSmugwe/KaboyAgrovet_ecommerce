# app_final.py - Final Working Flask Admin with Manual Sales
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import BaseView, expose
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kaboy_agrovet_final.db'
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
    column_list = ['name', 'category', 'description', 'image_url', 'variants_count']
    column_labels = {
        'name': 'Product Name',
        'category': 'Category',
        'description': 'Description',
        'image_url': 'Image',
        'variants_count': 'Variants'
    }
    form_columns = ['name', 'category', 'description', 'image_url']
    column_searchable_list = ['name', 'category', 'description']
    column_filters = ['category', 'created_at']

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
    form_columns = ['product', 'quantity_value', 'quantity_unit', 'selling_price', 'buying_price', 'stock_level', 'expiry_date', 'supplier']
    column_searchable_list = ['product.name', 'supplier']
    column_filters = ['stock_level', 'expiry_date', 'supplier']

class OrderAdminView(MyAdminModelView):
    column_list = ['customer_name', 'customer_email', 'customer_phone', 'total_amount', 'ordered_at', 'payment_status', 'items_count']
    column_labels = {
        'customer_name': 'Customer Name',
        'customer_email': 'Email',
        'customer_phone': 'Phone',
        'total_amount': 'Total Amount',
        'ordered_at': 'Order Date',
        'payment_status': 'Payment Status',
        'items_count': 'Items Count'
    }
    form_columns = ['customer_name', 'customer_email', 'customer_phone', 'delivery_address', 'total_amount', 'payment_status']
    column_searchable_list = ['customer_name', 'customer_email', 'customer_phone']
    column_filters = ['payment_status', 'ordered_at']

class OrderItemAdminView(MyAdminModelView):
    column_list = ['order', 'variant', 'quantity', 'price_at_purchase']
    column_labels = {
        'order': 'Parent Order',
        'variant': 'Product Variant',
        'quantity': 'Quantity',
        'price_at_purchase': 'Price at Purchase'
    }
    form_columns = ['order', 'variant', 'quantity', 'price_at_purchase']

class OfflineSaleAdminView(MyAdminModelView):
    column_list = ['customer_name', 'total_cost', 'amount_paid', 'change_given', 'payment_mode', 'sale_date', 'items_count']
    column_labels = {
        'customer_name': 'Customer Name',
        'total_cost': 'Total Cost',
        'amount_paid': 'Amount Paid',
        'change_given': 'Change Given',
        'payment_mode': 'Payment Mode',
        'sale_date': 'Sale Date',
        'items_count': 'Items Count'
    }
    form_columns = ['customer_name', 'total_cost', 'amount_paid', 'change_given', 'payment_mode']
    column_searchable_list = ['customer_name', 'payment_mode']
    column_filters = ['payment_mode', 'sale_date']

class OfflineSaleItemAdminView(MyAdminModelView):
    column_list = ['offline_sale', 'variant', 'quantity', 'price_at_sale']
    column_labels = {
        'offline_sale': 'Parent Sale',
        'variant': 'Product Variant',
        'quantity': 'Quantity',
        'price_at_sale': 'Price at Sale'
    }
    form_columns = ['offline_sale', 'variant', 'quantity', 'price_at_sale']

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

class ManualSaleView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/manual_sale.html')

# --- ADMIN SETUP ---
admin = Admin(app, name='Kaboy Agrovet Admin', template_mode='bootstrap3', base_template='admin/master.html')

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

@app.route('/api/manual-sale', methods=['POST'])
def submit_manual_sale():
    try:
        data = request.get_json()
        
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
            variant_id = item_data['variant_id']
            quantity = int(item_data['quantity'])
            price = float(item_data['price'])
            
            sale_item = OfflineSaleItem(
                offline_sale_id=sale.id,
                product_variant_id=variant_id,
                quantity=quantity,
                price_at_sale=price
            )
            db.session.add(sale_item)
            
            # Update stock level
            variant = ProductVariant.query.get(variant_id)
            if variant:
                variant.stock_level = max(0, variant.stock_level - quantity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sale recorded successfully!',
            'sale_id': sale.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error recording sale: {str(e)}'
        }), 500

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create some sample data for testing
        if not Product.query.first():
            # Create sample products
            product1 = Product(name="NPK Fertilizer", category="Fertilizer", description="Complete fertilizer for all crops")
            product2 = Product(name="DAP Fertilizer", category="Fertilizer", description="Phosphate fertilizer for root development")
            product3 = Product(name="Seeds Mix", category="Seed", description="Mixed vegetable seeds")
            
            db.session.add_all([product1, product2, product3])
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
            
            db.session.add_all([variant1, variant2, variant3, variant4])
            db.session.commit()
            
            print("✅ Sample data created successfully!")
    
    app.run(debug=True) 