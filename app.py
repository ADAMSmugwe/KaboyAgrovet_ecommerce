import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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

    def __repr__(self):
        product_name = self.product.name if self.product else "N/A"
        return f'<Variant {self.quantity_value}{self.quantity_unit} of {product_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'quantity_value': self.quantity_value,
            'quantity_unit': self.quantity_unit,
            'selling_price': self.selling_price,
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

class ProductVariantInlineForm(FlaskForm):
    id = HiddenField()
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
    column_list = ['product', 'quantity_value', 'quantity_unit', 'selling_price', 'buying_price']
    form_columns = ['product', 'quantity_value', 'quantity_unit', 'selling_price', 'buying_price']
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


# --- ADMIN ADD VIEWS ---
admin.add_view(OrderAdminView(Order, db.session, name='Customer Orders'))
admin.add_view(ProductAdminView(Product, db.session, name='Products'))
admin.add_view(ProductVariantAdminView(ProductVariant, db.session, name='Product Variants'))
admin.add_view(MyAdminModelView(Testimonial, db.session, name='Testimonials'))
admin.add_view(MyAdminModelView(FAQ, db.session, name='FAQs'))
admin.add_view(MyAdminModelView(ContactMessage, db.session, name='Contact Messages'))
admin.add_view(OrderItemAdminView(OrderItem, db.session, name='Order Items'))


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

            total_amount += (selling_price_float * quantity_int)

            order_items.append(OrderItem(
                order_id=None, # This will be set after order creation
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

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)