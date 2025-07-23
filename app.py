import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta # Add this import at the top
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from wtforms import FloatField, StringField, HiddenField, SelectField, IntegerField
from wtforms.widgets import TextInput
from flask_admin import expose
from wtforms.widgets import Select # Added for ProductForm category
from flask_admin.form.widgets import Select2Widget # Added for ProductForm category
from sqlalchemy.orm import Session
from flask_admin import BaseView, expose # Ensure BaseView and expose are imported

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'kaboy_agrovet.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['FLASK_ADMIN_SWATCH'] = 'yeti'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

admin = Admin(app, name='Kaboy Agrovet Admin', template_mode='bootstrap3')

ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', generate_password_hash('admin123'))

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
        return f"Order {self.id} by {self.customer_name} - {self.total_amount} KSh"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
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

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_name = db.Column(db.String(100), nullable=False)
    author_position = db.Column(db.String(100))
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonial {self.id} {self.author_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'author_name': self.author_name,
            'author_position': self.author_position,
            'text': self.text,
            'image_url': self.image_url,
            'is_approved': self.is_approved,
            'created_at': self.created_at
        }

class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<FAQ {self.id} {self.question}>'

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'display_order': self.display_order
        }

class ProductVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', back_populates='variants')
    quantity_value = db.Column(db.Float, nullable=False)
    quantity_unit = db.Column(db.String(20), nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    buying_price = db.Column(db.Float, nullable=True)
    stock_level = db.Column(db.Integer, default=0, nullable=False)
    
    # ADD THESE TWO LINES:
    expiry_date = db.Column(db.DateTime, nullable=True) # Optional expiry date, can be None
    supplier = db.Column(db.String(100), nullable=True) # Optional supplier name, can be None

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
            # Include new fields in to_dict for API response
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None, # Format for JSON
            'supplier': self.supplier
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
        return f"{self.quantity} x {variant_info} @ KSh {self.price_at_purchase}"

class OfflineSale(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(100), nullable=True) # Optional for walk-in
    amount_paid = db.Column(db.Float, nullable=False)
    change_given = db.Column(db.Float, nullable=False)
    payment_mode = db.Column(db.String(50), nullable=False) # e.g., 'Cash', 'Mpesa'
    total_cost = db.Column(db.Float, nullable=False) # Calculated total of items sold
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to OfflineSaleItem (one-to-many)
    items_sold = db.relationship('OfflineSaleItem', backref='offline_sale', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        customer = self.customer_name if self.customer_name else "Walk-in"
        return f'<Offline Sale {self.id} by {customer} - Total: {self.total_cost} ({self.payment_mode})>'

    def __str__(self):
        customer = self.customer_name if self.customer_name else "Walk-in"
        return f"Offline Sale {self.id} by {customer} - KSh {self.total_cost:.2f} ({self.payment_mode})"

class OfflineSaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    offline_sale_id = db.Column(db.Integer, db.ForeignKey('offline_sale.id'), nullable=False) # Links to parent OfflineSale
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)

    # Relationship to ProductVariant to get details
    variant = db.relationship('ProductVariant', backref='offline_sale_items', lazy=True) 

    quantity = db.Column(db.Integer, nullable=False)
    price_at_sale = db.Column(db.Float, nullable=False) # Price at time of sale

    def __repr__(self):
        variant_info = f"{self.variant.product.name} ({self.variant.quantity_value}{self.variant.quantity_unit})" if self.variant and self.variant.product else "N/A"
        return f'<Offline Sale Item {self.id} - {self.quantity} x {variant_info}>'

    def __str__(self):
        variant_info = f"{self.quantity} x {self.variant.product.name} ({self.variant.quantity_value}{self.variant.quantity_unit})" if self.variant and self.variant.product else "N/A"
        return f"{self.quantity} x {variant_info} @ KSh {self.price_at_sale}"

class ProductVariantInlineForm(FlaskForm):
    id = HiddenField()  # <-- Ensure this line exists!
    quantity_value = FloatField('Quantity Value')
    quantity_unit = StringField('Unit', widget=TextInput())
    selling_price = FloatField('Selling Price')
    buying_price = FloatField('Buying Price')

# --- FLASK-ADMIN VIEWS ---
class MyAdminModelView(ModelView):
    def is_accessible(self):
        return session.get('admin_logged_in')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

    form_extra_fields = {
        'image': FileField('Upload Image')
    }

    form_args = {
        'image': {
            'validators': [FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')]
        }
    }

    def on_model_change(self, form, model, is_created):
        if hasattr(form, 'image') and form.image.data:
            file_data = form.image.data
            filename = secure_filename(file_data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_data.save(file_path)
            model.image_url = '/' + file_path.replace(os.sep, '/')
        elif hasattr(form, 'image') and not is_created and not form.image.data and model.image_url:
            pass
        super(MyAdminModelView, self).on_model_change(form, model, is_created)

class ProductAdminView(MyAdminModelView):
    column_list = ['name', 'category', 'description', 'image_url']
    form_columns = [
        'name',
        'category',
        'description',
        'image',
        'image_url',
    ]
    inline_models = [
        (ProductVariant, dict(
            form=ProductVariantInlineForm,
            form_columns=['quantity_value', 'quantity_unit', 'selling_price', 'buying_price']
        ))
    ]

class ProductVariantAdminView(MyAdminModelView):
    column_list = ['product', 'quantity_value', 'quantity_unit', 'selling_price', 'buying_price', 'stock_level'] # ADD 'stock_level' here
    form_columns = ['product', 'quantity_value', 'quantity_unit', 'selling_price', 'buying_price', 'stock_level'] # ADD 'stock_level' here
    column_labels = {
        'product': 'Associated Product'
    }
    form_ajax_refs = {
        'product': {
            'fields': ['name'],
            'page_size': 10,
            'get_label': lambda p: p.name
        }
    }

class OrderAdminView(MyAdminModelView):
    column_list = ['customer_name', 'customer_email', 'customer_phone', 'delivery_address', 'total_amount', 'ordered_at', 'items']
    column_labels = {
        'customer_name': 'Customer Name',
        'customer_email': 'Email',
        'customer_phone': 'Phone',
        'delivery_address': 'Address',
        'total_amount': 'Total',
        'ordered_at': 'Order Date',
        'items': 'Items Ordered'
    }
    form_columns = ['customer_name', 'customer_email', 'customer_phone', 'delivery_address', 'total_amount', 'payment_status']
    form_widget_args = {
        'total_amount': {
            'readonly': True
        }
    }
class OrderItemAdminView(MyAdminModelView):
    column_list = ['order', 'variant', 'quantity', 'price_at_purchase']
    column_labels = {
        'order': 'Parent Order',
        'variant': 'Product Variant',
        'quantity': 'Quantity',
        'price_at_purchase': 'Price at Purchase'
    }
    form_columns = ['order', 'variant', 'quantity', 'price_at_purchase']
    form_ajax_refs = {
        'order': {
            'fields': ['customer_name'],
            'get_label': lambda o: f"Order {o.id} by {o.customer_name}"
        },
        'variant': {
            'fields': ['quantity_value', 'quantity_unit'],
            'get_label': lambda v: f"{v.product.name} ({v.quantity_value}{v.quantity_unit})" if v.product else f"Variant {v.id}"
        }
    }

# --- Add new AdminViews for OfflineSale and OfflineSaleItem ---
class OfflineSaleAdminView(MyAdminModelView):
    column_list = ['customer_name', 'total_cost', 'amount_paid', 'change_given', 'payment_mode', 'sale_date', 'items_sold']
    column_labels = {
        'customer_name': 'Customer Name',
        'total_cost': 'Total Cost',
        'amount_paid': 'Amount Paid',
        'change_given': 'Change Given',
        'payment_mode': 'Payment Mode',
        'sale_date': 'Sale Date',
        'items_sold': 'Items Sold'
    }
    form_columns = ['customer_name', 'total_cost', 'amount_paid', 'change_given', 'payment_mode']

class OfflineSaleItemAdminView(MyAdminModelView):
    column_list = ['offline_sale', 'variant', 'quantity', 'price_at_sale']
    column_labels = {
        'offline_sale': 'Parent Sale',
        'variant': 'Product Variant',
        'quantity': 'Quantity',
        'price_at_sale': 'Price at Sale'
    }
    form_columns = ['offline_sale', 'product_variant_id', 'quantity', 'price_at_sale']
    # FIX: Use 'variant' (relationship) instead of 'product_variant_id' (column) for AJAX refs
    form_ajax_refs = {
        'offline_sale': {
            'fields': ['customer_name', 'sale_date'],
            'get_label': lambda s: f"Sale {s.id} by {s.customer_name or 'Walk-in'} on {s.sale_date.strftime('%Y-%m-%d')}"
        },
        'variant': {
            'fields': ['quantity_value', 'quantity_unit'],
            'get_label': lambda v: f"{v.product.name} ({v.quantity_value}{v.quantity_unit})" if v.product else f"Variant {v.id}"
        }
    }

class ManualSaleView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/manual_sale.html')

# --- ADMIN ADD VIEWS ---
admin.add_view(OrderAdminView(Order, db.session, name='Customer Orders'))
admin.add_view(ProductAdminView(Product, db.session, name='Products'))
admin.add_view(ProductVariantAdminView(ProductVariant, db.session, name='Product Variants'))
admin.add_view(MyAdminModelView(Testimonial, db.session, name='Testimonials'))
admin.add_view(MyAdminModelView(FAQ, db.session, name='FAQs'))
admin.add_view(MyAdminModelView(ContactMessage, db.session, name='Contact Messages'))
admin.add_view(OrderItemAdminView(OrderItem, db.session, name='Order Items'))
admin.add_view(OfflineSaleAdminView(OfflineSale, db.session, name='Offline Sales'))
admin.add_view(OfflineSaleItemAdminView(OfflineSaleItem, db.session, name='Offline Sale Items'))
admin.add_view(ManualSaleView(name='Manual Sales', endpoint='manual_sale')) # Add this line


# --- ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

# REMOVED: @app.route('/submit-order', methods=['POST']) def submit_order(): ...

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

@app.route('/api/testimonials')
def get_testimonials():
    testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
    return jsonify([t.to_dict() for t in testimonials])

@app.route('/api/faqs')
def get_faqs():
    faqs = FAQ.query.order_by(FAQ.display_order, FAQ.id).all()
    return jsonify([f.to_dict() for f in faqs])

@app.route('/api/contact', methods=['POST'])
def submit_contact_message():
    try:
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form['message']

        if not all([name, email, message]):
            return jsonify({'status': 'error', 'message': 'Name, email, and message are required.'}), 400

        new_contact = ContactMessage(
            name=name,
            email=email,
            phone=phone if phone is not None else '',
            subject=subject if subject is not None else '',
            message=message
        )
        db.session.add(new_contact)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Message sent successfully!'}), 200
    except Exception as e:
        print(f"Error processing contact message: {e}")
        return jsonify({'status': 'error', 'message': 'There was an error sending your message. Please try again later.'}), 500

@app.route('/api/submit-full-order', methods=['POST'])
def submit_full_order():
    try:
        data = request.json

        customer_name = data.get('customer_name')
        customer_email = data.get('customer_email')
        customer_phone = data.get('customer_phone')
        delivery_address = data.get('delivery_address')
        items_data = data.get('items', [])

        if not all([customer_name, customer_email, customer_phone, delivery_address]):
            return jsonify({'status': 'error', 'message': 'Customer details (name, email, phone, address) are required.'}), 400
        if not items_data:
            return jsonify({'status': 'error', 'message': 'Cart is empty. No items to order.'}), 400

        total_amount = 0.0
        order_items = []

        # Process each item in the cart
        for item_data in items_data:
            product_variant_id = item_data.get('product_variant_id')
            quantity = item_data.get('quantity')
            selling_price = item_data.get('selling_price')

            if not all([product_variant_id, quantity, selling_price]):
                return jsonify({'status': 'error', 'message': 'Invalid item data in cart.'}), 400

            try:
                quantity_int = int(quantity)
                selling_price_float = float(selling_price)
                if quantity_int <= 0 or selling_price_float < 0:
                    raise ValueError("Invalid quantity or price for item.")
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid quantity or price format for an item.'}), 400

            # --- NEW: Check and Deduct Stock Level ---
            variant = db.session.get(ProductVariant, product_variant_id)
            if not variant:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': f'Product variant with ID {product_variant_id} not found.'}), 400

            if variant.stock_level < quantity_int:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': f'Not enough stock for {variant.product.name} ({variant.quantity_value}{variant.quantity_unit}). Available: {variant.stock_level}'}), 400

            variant.stock_level -= quantity_int
            print(f"Stock for variant {variant.id} reduced to {variant.stock_level}")
            # --- END NEW Stock Deduction ---

            total_amount += (selling_price_float * quantity_int)

            order_items.append(OrderItem(
                product_variant_id=product_variant_id,
                quantity=quantity_int,
                price_at_purchase=selling_price_float
            ))

        new_order = Order(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            delivery_address=delivery_address,
            total_amount=total_amount,
            items=order_items
        )
        db.session.add(new_order)
        db.session.commit()

        # Update order_items to link to the new order
        for item in order_items:
            item.order_id = new_order.id
        db.session.commit()

        return jsonify({'status': 'success', 'message': f'Order {new_order.id} placed successfully! Total: KSh {total_amount:.2f}'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error submitting full order: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Failed to complete order. Please try again later.'}), 500

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Incorrect password')
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    orders = Order.query.order_by(Order.ordered_at.desc()).all()

    return render_template('admin_dashboard.html', orders=orders)

# Add a new route for the manual sales page (accessible only by admin)
@app.route('/admin/manual-sale')
def manual_sale_page():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin/manual_sale.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/api/manual-sale', methods=['POST'])
def api_manual_sale():
    if not session.get('admin_logged_in'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        data = request.json
        customer_name = data.get('customer_name')
        amount_paid = data.get('amount_paid')
        change_given = data.get('change_given')
        payment_mode = data.get('payment_mode')
        total_cost = data.get('total_cost')
        items_sold = data.get('items_sold', [])

        # Validate required fields
        if amount_paid is None or change_given is None or payment_mode is None or total_cost is None or not items_sold:
            return jsonify({'status': 'error', 'message': 'Missing required sale details.'}), 400

        # Create OfflineSale
        sale = OfflineSale(
            customer_name=customer_name,
            amount_paid=amount_paid,
            change_given=change_given,
            payment_mode=payment_mode,
            total_cost=total_cost
        )
        db.session.add(sale)
        db.session.flush()  # Get sale.id before committing

        # Add items and deduct stock
        for item in items_sold:
            variant_id = item.get('product_variant_id')
            quantity = item.get('quantity')
            price_at_sale = item.get('price_at_sale')
            if not variant_id or not quantity or price_at_sale is None:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': 'Invalid item data.'}), 400
            variant = db.session.get(ProductVariant, variant_id)
            if not variant:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': f'Product variant ID {variant_id} not found.'}), 400
            if variant.stock_level < quantity:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': f'Not enough stock for {variant.product.name} ({variant.quantity_value}{variant.quantity_unit}). Available: {variant.stock_level}'}), 400
            variant.stock_level -= quantity
            sale_item = OfflineSaleItem(
                offline_sale_id=sale.id,
                product_variant_id=variant_id,
                quantity=quantity,
                price_at_sale=price_at_sale
            )
            db.session.add(sale_item)

        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Sale recorded successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error saving manual sale: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to record sale. Please try again.'}), 500

# --- NEW: API Endpoints for Dashboard Charts Data ---
@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    try:
        # Total Sales (from online orders)
        total_online_sales = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0.0

        # Total Sales (from offline sales) with SQL-level NULL handling
        total_offline_sales = db.session.query(
            db.func.coalesce(db.func.sum(OfflineSale.total_cost), 0.0)
        ).scalar()

        # Get count of offline sale items
        offline_sales_items_count = db.session.query(
            db.func.sum(OfflineSaleItem.quantity)
        ).scalar() or 0

        total_sales = total_online_sales + total_offline_sales

        # Low Stock Alerts (ProductVariants with stock_level < 10, adjust threshold as needed)
        low_stock_variants = ProductVariant.query.filter(ProductVariant.stock_level < 10).all()
        low_stock_count = len(low_stock_variants)  # Define low_stock_count here
        low_stock_items = []
        
        for v in low_stock_variants:
            product = v.product
            if product:
                low_stock_items.append({
                    'id': v.id,
                    'name': product.name,
                    'variant': f"{v.quantity_value}{v.quantity_unit}",
                    'stock': v.stock_level,
                    'category': product.category,
                    'selling_price': v.selling_price,
                    'expiry_date': v.expiry_date.strftime('%Y-%m-%d') if v.expiry_date else None,
                })

        # Total Inventory Value (sum of selling_price * stock_level for all variants)
        total_inventory_value = db.session.query(db.func.sum(ProductVariant.selling_price * ProductVariant.stock_level)).scalar() or 0

        # Total Orders (online)
        total_online_orders = Order.query.count()

        # Total Offline Sales (transactions)
        total_offline_transactions = OfflineSale.query.count()

        # Today's Orders (online)
        today = datetime.utcnow().date()
        todays_online_orders = Order.query.filter(db.func.date(Order.ordered_at) == today).count()

        # Today's Offline Sales (transactions)
        todays_offline_sales = OfflineSale.query.filter(db.func.date(OfflineSale.sale_date) == today).count()

        return jsonify({
            'total_sales': float(total_sales),
            'low_stock_count': low_stock_count,
            'total_inventory_value': float(total_inventory_value),
            'total_online_orders': total_online_orders,
            'total_offline_transactions': total_offline_transactions,
            'offline_sales_items_count': offline_sales_items_count,  # New field
            'todays_online_orders': todays_online_orders,
            'todays_offline_sales': todays_offline_sales,
            'low_stock_items': low_stock_items  # Enhanced low stock items data
        })
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        db.session.rollback()  # Ensure session is rolled back on error
        return jsonify({
            'status': 'error',
            'message': 'Failed to load dashboard statistics'
        }), 500

@app.route('/api/dashboard/sales-trends')
def get_sales_trends():
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Online Sales
    online_sales_data = db.session.query(
        db.func.date(Order.ordered_at),
        db.func.sum(Order.total_amount)
    ).filter(Order.ordered_at >= thirty_days_ago).group_by(db.func.date(Order.ordered_at)).all()

    # Offline Sales
    offline_sales_data = db.session.query(
        db.func.date(OfflineSale.sale_date),
        db.func.sum(OfflineSale.total_cost)
    ).filter(OfflineSale.sale_date >= thirty_days_ago).group_by(db.func.date(OfflineSale.sale_date)).all()

    # Combine and format data
    sales_by_date = {}
    # Fix: db.func.date returns a string, not a date object
    for date, amount in online_sales_data:
        sales_by_date[str(date)] = sales_by_date.get(str(date), 0) + float(amount)
    for date, amount in offline_sales_data:
        sales_by_date[str(date)] = sales_by_date.get(str(date), 0) + float(amount)

    labels = [(datetime.utcnow() - timedelta(days=i)).date().isoformat() for i in range(30)][::-1]
    data = [sales_by_date.get(label, 0) for label in labels]

    return jsonify({
        'labels': labels,
        'data': data
    })

@app.route('/api/dashboard/stock-levels')
def get_stock_levels():
    # Get top 10 products by current stock level (or all if less than 10)
    variants = ProductVariant.query.order_by(ProductVariant.stock_level.desc()).limit(10).all()

    labels = []
    data = []
    for v in variants:
        labels.append(f"{v.product.name} ({v.quantity_value}{v.quantity_unit})")
        data.append(v.stock_level)

    return jsonify({
        'labels': labels,
        'data': data
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)