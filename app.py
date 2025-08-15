# app.py (COMPLETELY REPLACE WITH THIS CONTENT)
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
from flask_admin.form import Select2Field
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
app.config['FLASK_ADMIN_CUSTOM_CSS'] = 'static/css/flask_admin_custom.css'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

def send_order_notification(order):
    """Send email notification for new orders"""
    try:
        if not app.config['MAIL_USERNAME']:
            return  # Skip if email not configured
        
        msg = Message(
            f'New Order #{order.id} - Kaboy Agrovet',
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]  # Send to admin
        )
        
        msg.body = f"""
New order received!

Order ID: {order.id}
Customer: {order.customer_name}
Email: {order.customer_email}
Phone: {order.customer_phone}
Address: {order.delivery_address}
Total Amount: KSh {order.total_amount:.2f}
Order Date: {order.ordered_at.strftime('%Y-%m-%d %H:%M')}

Items:
{chr(10).join([f"- {item.quantity}x {item.variant.product.name} ({item.variant.quantity_value}{item.variant.quantity_unit}) @ KSh {item.price_at_purchase:.2f}" for item in order.items])}

Please process this order promptly.
        """
        
        mail.send(msg)
        print(f"Order notification email sent for order {order.id}")
    except Exception as e:
        print(f"Failed to send order notification email: {e}")

def send_low_stock_alert(variant):
    """Send email alert for low stock items"""
    try:
        if not app.config['MAIL_USERNAME']:
            return  # Skip if email not configured
        
        msg = Message(
            f'Low Stock Alert - {variant.product.name}',
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]  # Send to admin
        )
        
        msg.body = f"""
Low Stock Alert!

Product: {variant.product.name}
Variant: {variant.quantity_value}{variant.quantity_unit}
Current Stock: {variant.stock_level}
Selling Price: KSh {variant.selling_price:.2f}

Please restock this item soon to avoid running out of inventory.
        """
        
        mail.send(msg)
        print(f"Low stock alert email sent for {variant.product.name}")
    except Exception as e:
        print(f"Failed to send low stock alert email: {e}")

def generate_reset_token():
    """Generate a secure random token for password reset"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def send_password_reset_email(user, reset_url):
    """Send password reset email to user"""
    try:
        if not app.config['MAIL_USERNAME']:
            return False
        
        msg = Message(
            'Password Reset Request - Kaboy Agrovet Admin',
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email]
        )
        
        msg.html = render_template('emails/password_reset.html', 
                                 user=user, 
                                 reset_url=reset_url,
                                 expiry_hours=24)
        
        mail.send(msg)
        print(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
        return False

def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    try:
        if not app.config['MAIL_USERNAME']:
            return False
        
        msg = Message(
            f'Order Confirmation #{order.id} - Kaboy Agrovet',
            sender=app.config['MAIL_USERNAME'],
            recipients=[order.customer_email]
        )
        
        msg.html = render_template('emails/order_confirmation.html', order=order)
        
        mail.send(msg)
        print(f"Order confirmation email sent to {order.customer_email}")
        return True
    except Exception as e:
        print(f"Failed to send order confirmation email: {e}")
        return False

def send_marketing_email(subject, content, recipients, campaign_type='newsletter'):
    """Send marketing email to multiple recipients"""
    try:
        if not app.config['MAIL_USERNAME']:
            return False
        
        # Create campaign record
        campaign = EmailCampaign(
            subject=subject,
            content=content,
            recipient_count=len(recipients),
            campaign_type=campaign_type
        )
        db.session.add(campaign)
        db.session.commit()
        
        success_count = 0
        for recipient in recipients:
            try:
                msg = Message(
                    subject,
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[recipient.email]
                )
                
                msg.html = render_template('emails/marketing_template.html', 
                                         content=content,
                                         recipient=recipient,
                                         campaign=campaign)
                
                mail.send(msg)
                success_count += 1
                print(f"Marketing email sent to {recipient.email}")
            except Exception as e:
                print(f"Failed to send marketing email to {recipient.email}: {e}")
        
        # Update campaign with actual success count
        campaign.recipient_count = success_count
        db.session.commit()
        
        return success_count
    except Exception as e:
        print(f"Failed to send marketing email campaign: {e}")
        return 0

def generate_unsubscribe_token():
    """Generate a secure unsubscribe token"""
    return secrets.token_urlsafe(32)

@app.route('/api/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    """Subscribe to newsletter"""
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name', '')
        
        if not email:
            return jsonify({'status': 'error', 'message': 'Email is required.'}), 400
        
        # Check if already subscribed
        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            if existing.is_active:
                return jsonify({'status': 'error', 'message': 'Email is already subscribed.'}), 400
            else:
                # Reactivate subscription
                existing.is_active = True
                existing.name = name
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Newsletter subscription reactivated!'}), 200
        
        # Create new subscription
        unsubscribe_token = generate_unsubscribe_token()
        subscriber = NewsletterSubscriber(
            email=email,
            name=name,
            unsubscribe_token=unsubscribe_token
        )
        db.session.add(subscriber)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Successfully subscribed to newsletter!'}), 200
        
    except Exception as e:
        print(f"Error subscribing to newsletter: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to subscribe. Please try again.'}), 500

@app.route('/api/newsletter/unsubscribe/<token>')
def unsubscribe_newsletter(token):
    """Unsubscribe from newsletter"""
    try:
        subscriber = NewsletterSubscriber.query.filter_by(unsubscribe_token=token).first()
        if subscriber:
            subscriber.is_active = False
            db.session.commit()
            return render_template('newsletter_unsubscribed.html')
        else:
            return render_template('newsletter_unsubscribed.html', error=True)
    except Exception as e:
        print(f"Error unsubscribing from newsletter: {e}")
        return render_template('newsletter_unsubscribed.html', error=True)

@app.route('/admin/send-marketing-email', methods=['GET', 'POST'])
def send_marketing_email_route():
    """Admin route to send marketing emails"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        try:
            subject = request.form.get('subject')
            content = request.form.get('content')
            campaign_type = request.form.get('campaign_type', 'newsletter')
            
            if not subject or not content:
                flash('Subject and content are required.', 'error')
                return redirect(url_for('send_marketing_email_route'))
            
            # Get active subscribers
            subscribers = NewsletterSubscriber.query.filter_by(is_active=True).all()
            
            if not subscribers:
                flash('No active subscribers found.', 'error')
                return redirect(url_for('send_marketing_email_route'))
            
            # Send marketing email
            success_count = send_marketing_email(subject, content, subscribers, campaign_type)
            
            if success_count > 0:
                flash(f'Marketing email sent successfully to {success_count} subscribers!', 'success')
            else:
                flash('Failed to send marketing email.', 'error')
            
            return redirect(url_for('send_marketing_email_route'))
            
        except Exception as e:
            print(f"Error sending marketing email: {e}")
            flash('An error occurred while sending the email.', 'error')
            return redirect(url_for('send_marketing_email_route'))
    
    # Get subscriber count
    subscriber_count = NewsletterSubscriber.query.filter_by(is_active=True).count()
    
    return render_template('admin_send_marketing_email.html', subscriber_count=subscriber_count)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

    def __str__(self):
        return f'{self.name} ({self.category})'

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

    def __str__(self):
        product_name = self.product.name if self.product else "N/A"
        return f'{product_name} - {self.quantity_value}{self.quantity_unit}'

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity_value': self.quantity_value,
            'quantity_unit': self.quantity_unit,
            'selling_price': self.selling_price,
            'buying_price': self.buying_price,
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
        customer = self.customer_name if self.customer_name else "Walk-in"
        return f'<Offline Sale {self.id} by {customer} - Total: {self.total_cost} ({self.payment_mode})>'

    def __str__(self):
        customer = self.customer_name if self.customer_name else "Walk-in"
        return f"Offline Sale {self.id} by {customer} - KSh {self.total_cost:.2f} ({self.payment_mode})"
    
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

class NewsletterSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100))
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    unsubscribe_token = db.Column(db.String(255), unique=True)

    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'

class EmailCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipient_count = db.Column(db.Integer, default=0)
    campaign_type = db.Column(db.String(50), default='newsletter')  # newsletter, promotion, announcement

    def __repr__(self):
        return f'<EmailCampaign {self.id} - {self.subject}>'

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f'<AdminUser {self.username}>'

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PasswordResetToken {self.id} for user {self.user_id}>'
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        return not self.used and not self.is_expired()



# --- ADVANCED ANALYTICS MODELS ---
class CustomerAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(100))
    total_orders = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    first_order_date = db.Column(db.DateTime)
    last_order_date = db.Column(db.DateTime)
    average_order_value = db.Column(db.Float, default=0.0)
    customer_lifetime_value = db.Column(db.Float, default=0.0)
    preferred_categories = db.Column(db.JSON)  # Store as JSON array
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CustomerAnalytics {self.customer_email} - CLV: {self.customer_lifetime_value}>'

class ProductAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)
    total_sold = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    average_rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    days_in_stock = db.Column(db.Integer, default=0)
    stockout_days = db.Column(db.Integer, default=0)
    profit_margin = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    variant = db.relationship('ProductVariant', backref='analytics')
    
    def __repr__(self):
        variant_info = f"{self.variant.product.name} ({self.variant.quantity_value}{self.variant.quantity_unit})" if self.variant and self.variant.product else "N/A"
        return f'<ProductAnalytics {variant_info} - Revenue: {self.total_revenue}>'

class SalesAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    total_orders = db.Column(db.Integer, default=0)
    total_sales = db.Column(db.Float, default=0.0)
    total_offline_sales = db.Column(db.Float, default=0.0)
    total_online_sales = db.Column(db.Float, default=0.0)
    average_order_value = db.Column(db.Float, default=0.0)
    unique_customers = db.Column(db.Integer, default=0)
    top_selling_products = db.Column(db.JSON)  # Store as JSON array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SalesAnalytics {self.date} - Sales: {self.total_sales}>'



# WTForm for ProductVariant inline editing
class ProductVariantInlineForm(FlaskForm):
    id = HiddenField()
    quantity_value = FloatField('Quantity Value', validators=[DataRequired()])
    quantity_unit = StringField('Unit', validators=[DataRequired()])
    selling_price = FloatField('Selling Price', validators=[DataRequired()])
    buying_price = FloatField('Buying Price')
    stock_level = IntegerField('Stock Level', validators=[DataRequired()])
    expiry_date = DateTimeField('Expiry Date', format='%Y-%m-%d')
    supplier = StringField('Supplier')

# Custom Form for Product (to use SelectField for category)
class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Fertilizer', 'Fertilizer'),
        ('Pesticide', 'Pesticide'),
        ('Seed', 'Seed'),
        ('Feed', 'Feed'),
        ('Other', 'Other')
    ], widget=Select(), validators=[DataRequired()])
    description = StringField('Description')
    image = FileField('Upload Image')
    image_url = StringField('Image URL')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# --- FLASK-ADMIN VIEWS ---
class MyAdminModelView(ModelView):
    def is_accessible(self):
        return True  # Temporarily allow access without authentication
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))
    
    # Enable all CRUD operations
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    
    def scaffold_form(self):
        """Override to ensure form_choices are properly handled"""
        form_class = super().scaffold_form()
        
        # Ensure form_choices are properly formatted for Flask-Admin
        if hasattr(self, 'form_choices'):
            for field_name, choices in self.form_choices.items():
                if hasattr(form_class, field_name):
                    field = getattr(form_class, field_name)
                    # Convert 2-tuples to 4-tuples if needed
                    formatted_choices = []
                    for choice in choices:
                        if len(choice) == 2:
                            formatted_choices.append((choice[0], choice[1], False, {}))
                        else:
                            formatted_choices.append(choice)
                    field.choices = formatted_choices
        
        return form_class
    
    def get_create_form(self):
        """Override to handle form creation with proper context"""
        form_class = super().get_create_form()
        
        # Fix any choice fields that might have incorrect tuple lengths
        for field_name in dir(form_class):
            field = getattr(form_class, field_name)
            if hasattr(field, 'choices') and field.choices:
                # Check if any choices have incorrect tuple lengths
                needs_fixing = False
                for choice in field.choices:
                    if len(choice) == 3:  # 3-tuple instead of 4-tuple
                        needs_fixing = True
                        break
                
                if needs_fixing:
                    formatted_choices = []
                    for choice in field.choices:
                        if len(choice) == 2:
                            formatted_choices.append((choice[0], choice[1], False, {}))
                        elif len(choice) == 3:
                            formatted_choices.append((choice[0], choice[1], choice[2], {}))
                        else:
                            formatted_choices.append(choice)
                    field.choices = formatted_choices
        
        return form_class
    
    def get_edit_form(self):
        """Override to handle form creation with proper context"""
        form_class = super().get_edit_form()
        
        # Fix any choice fields that might have incorrect tuple lengths
        for field_name in dir(form_class):
            field = getattr(form_class, field_name)
            if hasattr(field, 'choices') and field.choices:
                # Check if any choices have incorrect tuple lengths
                needs_fixing = False
                for choice in field.choices:
                    if len(choice) == 3:  # 3-tuple instead of 4-tuple
                        needs_fixing = True
                        break
                
                if needs_fixing:
                    formatted_choices = []
                    for choice in field.choices:
                        if len(choice) == 2:
                            formatted_choices.append((choice[0], choice[1], False, {}))
                        elif len(choice) == 3:
                            formatted_choices.append((choice[0], choice[1], choice[2], {}))
                        else:
                            formatted_choices.append(choice)
                    field.choices = formatted_choices
        
        return form_class

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
    
    # Disable modals to use full-page forms
    create_modal = False
    edit_modal = False
    
    # Ensure forms are accessible
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    
    # Add column formatter for variants_count
    column_formatters = {
        'variants_count': lambda v, c, m, p: len(m.variants) if m.variants else 0
    }

    # Clean fix: Use form_overrides to force SelectField for category
    form_overrides = {
        'category': SelectField
    }

    form_choices = {
        'category': [
            ('Fertilizer', 'Fertilizer'),
            ('Pesticide', 'Pesticide'),
            ('Seed', 'Seed'),
            ('Feed', 'Feed'),
            ('Other', 'Other')
        ]
    }

# Simple ModelView classes - removed complex custom views

class ProductVariantForm(FlaskForm):
    """Custom form for ProductVariant to avoid Select2Widget issues"""
    product = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity_value = FloatField('Quantity Value', validators=[DataRequired()])
    quantity_unit = SelectField('Unit', choices=[
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
    ], validators=[DataRequired()])
    selling_price = FloatField('Selling Price', validators=[DataRequired()])
    buying_price = FloatField('Buying Price')
    stock_level = IntegerField('Stock Level', validators=[DataRequired()])
    expiry_date = DateTimeField('Expiry Date', format='%Y-%m-%d')
    supplier = StringField('Supplier')

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
    create_modal = False
    edit_modal = False
    
        # Fix: Use form_overrides to properly configure the product field
    form_overrides = {
        'product': SelectField
    }

    def get_create_form(self):
        """Override to populate product choices dynamically"""
        form_class = super().get_create_form()

        # Populate product choices when the form is actually used
        try:
            products = Product.query.order_by(Product.name).all()
            product_choices = [(p.id, p.name) for p in products]
            formatted_choices = []
            for choice in product_choices:
                formatted_choices.append((choice[0], choice[1], False, {}))
            form_class.product.choices = formatted_choices
        except:
            # Fallback if database is not available
            form_class.product.choices = []

        return form_class

    def get_edit_form(self):
        """Override to populate product choices dynamically"""
        form_class = super().get_edit_form()

        # Populate product choices when the form is actually used
        try:
            products = Product.query.order_by(Product.name).all()
            product_choices = [(p.id, p.name) for p in products]
            formatted_choices = []
            for choice in product_choices:
                formatted_choices.append((choice[0], choice[1], False, {}))
            form_class.product.choices = formatted_choices
        except:
            # Fallback if database is not available
            form_class.product.choices = []

        return form_class

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
    
    # Add column formatter for items_count
    column_formatters = {
        'items_count': lambda v, c, m, p: len(m.items) if m.items else 0
    }
    
    form_widget_args = {
        'total_amount': {
            'readonly': True
        }
    }
    
    # Add proper form configuration
    form_args = {
        'customer_name': {
            'validators': [DataRequired()]
        },
        'customer_email': {
            'validators': [DataRequired(), Email()]
        },
        'customer_phone': {
            'validators': [DataRequired()]
        },
        'delivery_address': {
            'validators': [DataRequired()]
        }
    }
    
    # Fix: Use form_overrides to properly configure the payment_status field
    form_overrides = {
        'payment_status': SelectField
    }

    form_choices = {
        'payment_status': [
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Cancelled', 'Cancelled'),
            ('Refunded', 'Refunded')
        ]
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
    # Removed form_ajax_refs to fix the choice unpacking issue
    
    # Add proper form configuration
    form_args = {
        'quantity': {
            'validators': [DataRequired()]
        },
        'price_at_purchase': {
            'validators': [DataRequired()]
        }
    }
    


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
    
    # Add column formatter for items_count
    column_formatters = {
        'items_count': lambda v, c, m, p: len(m.items_sold) if m.items_sold else 0
    }
    
    # Add proper form configuration
    form_args = {
        'customer_name': {
            'validators': [DataRequired()]
        },
        'total_cost': {
            'validators': [DataRequired()]
        },
        'amount_paid': {
            'validators': [DataRequired()]
        },
        'change_given': {
            'validators': [DataRequired()]
        }
    }
    
    # Fix: Use form_overrides to properly configure the payment_mode field
    form_overrides = {
        'payment_mode': SelectField
    }

    form_choices = {
        'payment_mode': [
            ('Cash', 'Cash'),
            ('M-Pesa', 'M-Pesa'),
            ('Bank Transfer', 'Bank Transfer'),
            ('Card', 'Card'),
            ('Other', 'Other')
        ]
    }

class OfflineSaleItemAdminView(MyAdminModelView):
    column_list = ['offline_sale', 'variant', 'quantity', 'price_at_sale']
    column_labels = {
        'offline_sale': 'Parent Sale',
        'variant': 'Product Variant',
        'quantity': 'Quantity',
        'price_at_sale': 'Price at Sale'
    }
    form_columns = ['offline_sale', 'variant', 'quantity', 'price_at_sale']
    # Removed form_ajax_refs to fix the choice unpacking issue
    
    # Add proper form configuration
    form_args = {
        'quantity': {
            'validators': [DataRequired()]
        },
        'price_at_sale': {
            'validators': [DataRequired()]
        }
    }
    






# --- ANALYTICS ADMIN VIEWS ---
class CustomerAnalyticsAdminView(MyAdminModelView):
    column_list = ['customer_email', 'customer_name', 'total_orders', 'total_spent', 'customer_lifetime_value', 'last_updated']
    column_labels = {
        'customer_email': 'Email',
        'customer_name': 'Name',
        'total_orders': 'Total Orders',
        'total_spent': 'Total Spent',
        'customer_lifetime_value': 'CLV',
        'last_updated': 'Last Updated'
    }
    form_columns = ['customer_email', 'customer_name', 'total_orders', 'total_spent', 'customer_lifetime_value']
    column_searchable_list = ['customer_email', 'customer_name']
    column_filters = ['last_updated']
    can_create = False  # Analytics are auto-generated
    can_delete = False

class ProductAnalyticsAdminView(MyAdminModelView):
    column_list = ['variant', 'total_sold', 'total_revenue', 'profit_margin', 'last_updated']
    column_labels = {
        'variant': 'Product Variant',
        'total_sold': 'Total Sold',
        'total_revenue': 'Total Revenue',
        'profit_margin': 'Profit Margin %',
        'last_updated': 'Last Updated'
    }
    form_columns = ['variant', 'total_sold', 'total_revenue', 'profit_margin']
    # Removed form_ajax_refs to fix the choice unpacking issue
    column_filters = ['last_updated']
    can_create = False  # Analytics are auto-generated
    can_delete = False
    


class SalesAnalyticsAdminView(MyAdminModelView):
    column_list = ['date', 'total_orders', 'total_sales', 'average_order_value', 'unique_customers']
    column_labels = {
        'date': 'Date',
        'total_orders': 'Total Orders',
        'total_sales': 'Total Sales',
        'average_order_value': 'Avg Order Value',
        'unique_customers': 'Unique Customers'
    }
    form_columns = ['date', 'total_orders', 'total_sales', 'average_order_value', 'unique_customers']
    column_filters = ['date']
    can_create = False  # Analytics are auto-generated
    can_delete = False

class ManualSaleView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/manual_sale.html')

# --- ENHANCED ADMIN VIEWS ---
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
    form_extra_fields = {
        'image': FileField('Upload Author Image')
    }
    column_searchable_list = ['author_name', 'text']
    column_filters = ['is_approved', 'created_at']
    
    # Add proper form configuration
    form_args = {
        'author_name': {
            'validators': [DataRequired()]
        },
        'text': {
            'validators': [DataRequired()]
        }
    }

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
    
    # Add proper form configuration
    form_args = {
        'question': {
            'validators': [DataRequired()]
        },
        'answer': {
            'validators': [DataRequired()]
        }
    }

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
    
    # Add proper form configuration
    form_args = {
        'name': {
            'validators': [DataRequired()]
        },
        'email': {
            'validators': [DataRequired(), Email()]
        },
        'message': {
            'validators': [DataRequired()]
        }
    }

# --- ADMIN SETUP ---
admin = Admin(app, name='Kaboy Agrovet Admin', template_mode='bootstrap3')

# Add admin views
admin.add_view(OrderAdminView(Order, db.session, name='Orders'))
admin.add_view(ProductAdminView(Product, db.session, name='Products'))
admin.add_view(ProductVariantAdminView(ProductVariant, db.session, name='Product Variants'))
admin.add_view(OrderItemAdminView(OrderItem, db.session, name='Order Items'))
admin.add_view(OfflineSaleAdminView(OfflineSale, db.session, name='Offline Sales'))
admin.add_view(OfflineSaleItemAdminView(OfflineSaleItem, db.session, name='Offline Sale Items'))
admin.add_view(TestimonialAdminView(Testimonial, db.session, name='Testimonials'))
admin.add_view(FAQAdminView(FAQ, db.session, name='FAQs'))
admin.add_view(ContactMessageAdminView(ContactMessage, db.session, name='Contact Messages'))
admin.add_view(ModelView(NewsletterSubscriber, db.session, name='Newsletter Subscribers'))
admin.add_view(ModelView(EmailCampaign, db.session, name='Email Campaigns'))
admin.add_view(ModelView(AdminUser, db.session, name='Admin Users'))
admin.add_view(ModelView(PasswordResetToken, db.session, name='Password Reset Tokens'))
admin.add_view(CustomerAnalyticsAdminView(CustomerAnalytics, db.session, name='Customer Analytics'))
admin.add_view(ProductAnalyticsAdminView(ProductAnalytics, db.session, name='Product Analytics'))
admin.add_view(SalesAnalyticsAdminView(SalesAnalytics, db.session, name='Sales Analytics'))

# --- ROUTES ---
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
    try:
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
            try:
                variant_data = variant.to_dict()
                # Safely access product attributes
                if variant.product:
                    variant_data['product_name'] = variant.product.name
                    variant_data['product_category'] = variant.product.category
                    variant_data['product_description'] = variant.product.description
                    variant_data['product_image_url'] = variant.product.image_url
                else:
                    variant_data['product_name'] = 'Unknown Product'
                    variant_data['product_category'] = 'Unknown'
                    variant_data['product_description'] = ''
                    variant_data['product_image_url'] = ''
                result.append(variant_data)
            except Exception as e:
                print(f"Error processing variant {variant.id}: {e}")
                continue
        
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_product_variants: {e}")
        return jsonify({'error': 'Failed to load product variants'}), 500

@app.route('/api/admin/product-variants')
def get_admin_product_variants():
    """Admin endpoint to get all product variants (including zero stock)"""
    try:
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
        
        # Don't filter by stock level for admin
        variants = query.all()
        
        result = []
        for variant in variants:
            try:
                variant_data = variant.to_dict()
                # Safely access product attributes
                if variant.product:
                    variant_data['product_name'] = variant.product.name
                    variant_data['product_category'] = variant.product.category
                    variant_data['product_description'] = variant.product.description
                    variant_data['product_image_url'] = variant.product.image_url
                else:
                    variant_data['product_name'] = 'Unknown Product'
                    variant_data['product_category'] = 'Unknown'
                    variant_data['product_description'] = ''
                    variant_data['product_image_url'] = ''
                result.append(variant_data)
            except Exception as e:
                print(f"Error processing variant {variant.id}: {e}")
                continue
        
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_admin_product_variants: {e}")
        return jsonify({'error': 'Failed to load product variants'}), 500

@app.route('/api/debug/product-variants')
def debug_product_variants():
    """Debug endpoint to check product variants"""
    try:
        # Test basic database connection
        variant_count = ProductVariant.query.count()
        product_count = Product.query.count()
        
        # Test a simple query
        variants = ProductVariant.query.limit(5).all()
        variant_data = []
        
        for variant in variants:
            try:
                data = {
                    'id': variant.id,
                    'product_id': variant.product_id,
                    'quantity_value': variant.quantity_value,
                    'quantity_unit': variant.quantity_unit,
                    'selling_price': variant.selling_price,
                    'stock_level': variant.stock_level,
                    'has_product': variant.product is not None,
                    'product_name': variant.product.name if variant.product else 'No Product'
                }
                variant_data.append(data)
            except Exception as e:
                variant_data.append({
                    'id': variant.id,
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'variant_count': variant_count,
            'product_count': product_count,
            'sample_variants': variant_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/testimonials')
def get_testimonials():
    testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
    return jsonify([t.to_dict() for t in testimonials])

@app.route('/api/faqs')
def get_faqs():
    faqs = FAQ.query.order_by(FAQ.display_order, FAQ.id).all()
    return jsonify([f.to_dict() for f in faqs])

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get current date and start of month
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Online Orders Stats
        total_orders = Order.query.count()
        monthly_orders = Order.query.filter(Order.ordered_at >= start_of_month).count()
        total_online_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        monthly_online_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.ordered_at >= start_of_month
        ).scalar() or 0
        
        # Offline Sales Stats
        total_offline_sales = OfflineSale.query.count()
        monthly_offline_sales = OfflineSale.query.filter(OfflineSale.sale_date >= start_of_month).count()
        total_offline_revenue = db.session.query(db.func.sum(OfflineSale.total_cost)).scalar() or 0
        monthly_offline_revenue = db.session.query(db.func.sum(OfflineSale.total_cost)).filter(
            OfflineSale.sale_date >= start_of_month
        ).scalar() or 0
        
        # Product Stats
        total_products = Product.query.count()
        total_variants = ProductVariant.query.count()
        low_stock_variants = ProductVariant.query.filter(ProductVariant.stock_level < 10).count()
        

        
        # Calculate profit (simplified)
        total_revenue = total_online_revenue + total_offline_revenue
        total_cogs = total_revenue * 0.6  # Simplified COGS calculation
        gross_profit = total_revenue - total_cogs
        net_profit = gross_profit  # No expenses to subtract
        
        monthly_revenue = monthly_online_revenue + monthly_offline_revenue
        monthly_cogs = monthly_revenue * 0.6
        monthly_gross_profit = monthly_revenue - monthly_cogs
        monthly_net_profit = monthly_gross_profit  # No expenses to subtract
        
        return jsonify({
            'status': 'success',
            'data': {
                'sales': {
                    'total_orders': total_orders,
                    'monthly_orders': monthly_orders,
                    'total_offline_sales': total_offline_sales,
                    'monthly_offline_sales': monthly_offline_sales,
                    'total_revenue': float(total_revenue),
                    'monthly_revenue': float(monthly_revenue)
                },
                'inventory': {
                    'total_products': total_products,
                    'total_variants': total_variants,
                    'low_stock_variants': low_stock_variants
                },
                'accounting': {
                    'gross_profit': float(gross_profit),
                    'monthly_gross_profit': float(monthly_gross_profit),
                    'net_profit': float(net_profit),
                    'monthly_net_profit': float(monthly_net_profit),
                    'profit_margin': float((net_profit / total_revenue * 100) if total_revenue > 0 else 0)
                }
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch dashboard statistics.'}), 500

@app.route('/api/dashboard/sales-trends')
def sales_trends():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get sales data for the last 7 days
        from datetime import datetime, timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Create date labels for the last 7 days
        labels = []
        data = []
        
        for i in range(7):
            current_date = end_date - timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            labels.insert(0, current_date.strftime('%b %d'))  # Insert at beginning for chronological order
            
            # Get online sales for this date
            online_sales = db.session.query(
                db.func.sum(Order.total_amount)
            ).filter(
                db.func.date(Order.ordered_at) == date_str
            ).scalar() or 0
            
            # Get offline sales for this date
            offline_sales = db.session.query(
                db.func.sum(OfflineSale.total_cost)
            ).filter(
                db.func.date(OfflineSale.sale_date) == date_str
            ).scalar() or 0
            
            # Total sales for this date
            total_sales = float(online_sales + offline_sales)
            data.insert(0, total_sales)  # Insert at beginning for chronological order
        
        return jsonify({
            'labels': labels,
            'data': data
        })
    except Exception as e:
        print(f"Error getting sales trends: {e}")
        return jsonify({'error': 'Failed to get sales trends'}), 500

@app.route('/api/dashboard/stock-levels')
def stock_levels():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get all product variants with their stock levels
        variants = ProductVariant.query.join(Product).order_by(Product.name).all()
        
        labels = []
        data = []
        low_stock_items = []
        
        for variant in variants:
            product_name = variant.product.name if variant.product else "Unknown"
            variant_info = f"{variant.quantity_value}{variant.quantity_unit}"
            label = f"{product_name} ({variant_info})"
            
            labels.append(label)
            data.append(variant.stock_level)
            
            # Track low stock items for the dashboard
            if variant.stock_level < 10:
                low_stock_items.append({
                    'product_name': product_name,
                    'variant_info': variant_info,
                    'stock_level': variant.stock_level,
                    'selling_price': variant.selling_price
                })
        
        return jsonify({
            'labels': labels,
            'data': data,
            'low_stock_items': low_stock_items
        })
    except Exception as e:
        print(f"Error getting stock levels: {e}")
        return jsonify({'error': 'Failed to get stock levels'}), 500

@app.route('/api/dashboard/recent-online-orders')
def recent_online_orders():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get recent online orders (last 10)
        recent_orders = Order.query.order_by(
            Order.ordered_at.desc()
        ).limit(10).all()
        
        orders_data = []
        for order in recent_orders:
            orders_data.append({
                'id': order.id,
                'customer_name': order.customer_name,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
                'total_amount': float(order.total_amount),
                'ordered_at': order.ordered_at.strftime('%Y-%m-%d %H:%M'),
                'payment_status': order.payment_status,
                'items_count': len(order.items)
            })
        
        return jsonify({'recent_orders': orders_data})
    except Exception as e:
        print(f"Error getting recent online orders: {e}")
        return jsonify({'error': 'Failed to get recent orders'}), 500

@app.route('/api/dashboard/recent-offline-sales')
def recent_offline_sales():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get recent offline sales (last 10)
        recent_sales = OfflineSale.query.order_by(
            OfflineSale.sale_date.desc()
        ).limit(10).all()
        
        sales_data = []
        for sale in recent_sales:
            sales_data.append({
                'id': sale.id,
                'customer_name': sale.customer_name or 'Walk-in',
                'total_cost': float(sale.total_cost),
                'amount_paid': float(sale.amount_paid),
                'change_given': float(sale.change_given),
                'payment_mode': sale.payment_mode,
                'sale_date': sale.sale_date.strftime('%Y-%m-%d %H:%M'),
                'items_count': len(sale.items_sold)
            })
        
        return jsonify({'recent_sales': sales_data})
    except Exception as e:
        print(f"Error getting recent offline sales: {e}")
        return jsonify({'error': 'Failed to get recent sales'}), 500

@app.route('/api/manual-sale', methods=['GET', 'POST'])
def submit_manual_sale():
    if request.method == 'GET':
        return jsonify({'message': 'Manual Sale API - Use POST method to submit data'})
    
    # POST method handling
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        
        # Extract sale data from modal form
        product_variant_id = data.get('product_variant_id')
        quantity = data.get('quantity')
        price = data.get('price')
        customer_name = data.get('customer_name', 'Walk-in customer')
        payment_mode = data.get('payment_mode')
        
        # Validation
        if not product_variant_id:
            return jsonify({'success': False, 'message': 'Product variant is required.'}), 400
        
        if not quantity or quantity <= 0:
            return jsonify({'success': False, 'message': 'Quantity must be greater than 0.'}), 400
        
        if not price or price <= 0:
            return jsonify({'success': False, 'message': 'Price must be greater than 0.'}), 400
        
        if not payment_mode:
            return jsonify({'success': False, 'message': 'Payment mode is required.'}), 400
        
        # Check if product variant exists
        variant = ProductVariant.query.get(product_variant_id)
        if not variant:
            return jsonify({'success': False, 'message': 'Product variant not found.'}), 400
        
        # Check stock availability
        quantity_int = int(quantity)
        if variant.stock_level < quantity_int:
            return jsonify({'success': False, 'message': f'Insufficient stock. Only {variant.stock_level} units available.'}), 400
        
        # Calculate total cost
        total_cost = quantity_int * price
        amount_paid = total_cost  # For manual sales, assume exact payment
        change_given = 0.0
        
        # Create offline sale
        new_sale = OfflineSale(
            customer_name=customer_name if customer_name != 'Walk-in customer' else None,
            total_cost=total_cost,
            amount_paid=amount_paid,
            change_given=change_given,
            payment_mode=payment_mode
        )
        
        # Create sale item
        sale_item = OfflineSaleItem(
            product_variant_id=product_variant_id,
            quantity=quantity_int,
            price_at_sale=price
        )
        
        new_sale.items_sold = [sale_item]
        
        # Update stock level
        variant.stock_level -= quantity_int
        
        db.session.add(new_sale)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Manual sale completed successfully! Sale ID: {new_sale.id}',
            'sale_id': new_sale.id,
            'total_amount': total_cost
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting manual sale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to complete sale. Please try again.'}), 500

@app.route('/api/restock-product', methods=['POST'])
def restock_product():
    """API endpoint to restock a product variant"""
    try:
        data = request.json
        variant_id = data.get('variant_id')
        quantity = data.get('quantity')
        
        if not variant_id or not quantity:
            return jsonify({'status': 'error', 'message': 'Variant ID and quantity are required.'}), 400
        
        try:
            quantity_int = int(quantity)
            if quantity_int <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid quantity format.'}), 400
        
        variant = ProductVariant.query.get(variant_id)
        if not variant:
            return jsonify({'status': 'error', 'message': 'Product variant not found.'}), 404
        
        # Update stock level
        variant.stock_level += quantity_int
        
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': f'Stock updated successfully. New stock level: {variant.stock_level}',
            'new_stock_level': variant.stock_level
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error restocking product: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to restock product. Please try again later.'}), 500







# --- ADVANCED ANALYTICS API ENDPOINTS ---
@app.route('/api/analytics/customer-insights', methods=['GET'])
def get_customer_insights():
    """Get customer analytics and insights"""
    try:
        # Get top customers by total spent
        top_customers = db.session.query(
            Order.customer_email,
            Order.customer_name,
            db.func.count(Order.id).label('order_count'),
            db.func.sum(Order.total_amount).label('total_spent'),
            db.func.avg(Order.total_amount).label('avg_order_value')
        ).group_by(Order.customer_email, Order.customer_name).order_by(
            db.func.sum(Order.total_amount).desc()
        ).limit(10).all()
        
        # Get customer acquisition over time
        customer_acquisition = db.session.query(
            db.func.date(Order.ordered_at).label('date'),
            db.func.count(db.func.distinct(Order.customer_email)).label('new_customers')
        ).group_by(db.func.date(Order.ordered_at)).order_by(
            db.func.date(Order.ordered_at).desc()
        ).limit(30).all()
        
        # Get customer categories
        customer_categories = db.session.query(
            db.func.count(db.func.distinct(Order.customer_email)).label('total_customers'),
            db.func.count(db.func.distinct(Order.customer_email)).filter(Order.ordered_at >= datetime.utcnow() - timedelta(days=30)).label('active_30_days'),
            db.func.count(db.func.distinct(Order.customer_email)).filter(Order.ordered_at >= datetime.utcnow() - timedelta(days=90)).label('active_90_days')
        ).first()
        
        return jsonify({
            'status': 'success',
            'data': {
                'top_customers': [
                    {
                        'email': customer[0],
                        'name': customer[1],
                        'order_count': customer[2],
                        'total_spent': float(customer[3]),
                        'avg_order_value': float(customer[4])
                    } for customer in top_customers
                ],
                'customer_acquisition': [
                    {
                        'date': str(acq[0]),
                        'new_customers': acq[1]
                    } for acq in customer_acquisition
                ],
                'customer_categories': {
                    'total_customers': customer_categories[0],
                    'active_30_days': customer_categories[1],
                    'active_90_days': customer_categories[2]
                }
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting customer insights: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to get customer insights.'}), 500

@app.route('/api/analytics/product-performance', methods=['GET'])
def get_product_performance():
    """Get product performance analytics"""
    try:
        # Get top selling products
        top_products = db.session.query(
            ProductVariant.id,
            Product.name,
            ProductVariant.quantity_value,
            ProductVariant.quantity_unit,
            db.func.sum(OrderItem.quantity).label('total_sold'),
            db.func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('total_revenue'),
            ProductVariant.stock_level
        ).join(Product).outerjoin(OrderItem).group_by(
            ProductVariant.id, Product.name
        ).order_by(db.func.sum(OrderItem.quantity).desc()).limit(10).all()
        
        # Get low stock products
        low_stock_products = ProductVariant.query.filter(
            ProductVariant.stock_level < 10
        ).join(Product).all()
        
        # Get product categories performance
        category_performance = db.session.query(
            Product.category,
            db.func.sum(OrderItem.quantity).label('total_sold'),
            db.func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('total_revenue')
        ).join(ProductVariant).join(OrderItem).group_by(
            Product.category
        ).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'top_products': [
                    {
                        'id': product[0],
                        'name': product[1],
                        'variant': f"{product[2]}{product[3]}",
                        'total_sold': product[4] or 0,
                        'total_revenue': float(product[5] or 0),
                        'stock_level': product[6]
                    } for product in top_products
                ],
                'low_stock_products': [
                    {
                        'id': product.id,
                        'name': product.product.name,
                        'variant': f"{product.quantity_value}{product.quantity_unit}",
                        'stock_level': product.stock_level,
                        'selling_price': product.selling_price
                    } for product in low_stock_products
                ],
                'category_performance': [
                    {
                        'category': cat[0],
                        'total_sold': cat[1] or 0,
                        'total_revenue': float(cat[2] or 0)
                    } for cat in category_performance
                ]
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting product performance: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to get product performance.'}), 500

@app.route('/api/analytics/sales-forecast', methods=['GET'])
def get_sales_forecast():
    """Get sales forecasting data"""
    try:
        # Get historical sales data for the last 90 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        daily_sales = db.session.query(
            db.func.date(Order.ordered_at).label('date'),
            db.func.sum(Order.total_amount).label('daily_sales'),
            db.func.count(Order.id).label('daily_orders')
        ).filter(
            Order.ordered_at >= start_date,
            Order.ordered_at <= end_date
        ).group_by(db.func.date(Order.ordered_at)).all()
        
        # Calculate trends
        if len(daily_sales) > 1:
            recent_sales = [float(sale[1]) for sale in daily_sales[-7:]]  # Last 7 days
            avg_daily_sales = sum(recent_sales) / len(recent_sales)
            
            # Simple trend calculation
            if len(recent_sales) >= 2:
                trend = (recent_sales[-1] - recent_sales[0]) / len(recent_sales)
            else:
                trend = 0
        else:
            avg_daily_sales = 0
            trend = 0
        
        # Generate forecast for next 30 days
        forecast = []
        current_date = end_date + timedelta(days=1)
        for i in range(30):
            forecast_date = current_date + timedelta(days=i)
            forecast_sales = avg_daily_sales + (trend * (i + 1))
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_sales': max(0, forecast_sales)
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'historical_sales': [
                    {
                        'date': str(sale[0]),
                        'sales': float(sale[1]),
                        'orders': sale[2]
                    } for sale in daily_sales
                ],
                'forecast': forecast,
                'metrics': {
                    'avg_daily_sales': avg_daily_sales,
                    'trend': trend,
                    'confidence_level': 'Medium'  # Placeholder
                }
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting sales forecast: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to get sales forecast.'}), 500



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

        # Check stock levels before processing
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

            # Check stock availability
            variant = ProductVariant.query.get(product_variant_id)
            if not variant:
                return jsonify({'status': 'error', 'message': f'Product variant {product_variant_id} not found.'}), 400
            
            if variant.stock_level < quantity_int:
                return jsonify({'status': 'error', 'message': f'Insufficient stock for {variant.product.name} ({variant.quantity_value}{variant.quantity_unit}). Available: {variant.stock_level}, Requested: {quantity_int}'}), 400

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
        
        # Update stock levels
        for item in order_items:
            variant = ProductVariant.query.get(item.product_variant_id)
            variant.stock_level -= item.quantity

        db.session.add(new_order)
        db.session.commit()
        
        # Send email notification to admin
        send_order_notification(new_order)
        
        # Send order confirmation email to customer
        send_order_confirmation_email(new_order)

        return jsonify({'status': 'success', 'message': f'Order {new_order.id} placed successfully! Total: KSh {total_amount:.2f}'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error submitting full order: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Failed to complete order. Please try again later.'}), 500

@app.route('/admin/test-email-page')
def test_email_page():
    """Serve the email test page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    config = {
        'server': app.config['MAIL_SERVER'],
        'port': app.config['MAIL_PORT'],
        'tls': app.config['MAIL_USE_TLS'],
        'username': app.config['MAIL_USERNAME'],
        'password': '***' if app.config['MAIL_PASSWORD'] else None
    }
    
    return render_template('admin_test_email.html', config=config)

@app.route('/admin/test-email')
def test_email():
    """Test route to verify email configuration is working"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Check if email is configured
        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
            return jsonify({
                'status': 'error',
                'message': 'Email not configured. Please set MAIL_USERNAME and MAIL_PASSWORD in your .env file.'
            }), 400
        
        # Create a test email
        msg = Message(
            'Test Email - Kaboy Agrovet Admin',
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]  # Send to admin email
        )
        
        msg.body = f"""
This is a test email from your Kaboy Agrovet admin system.

Email Configuration:
- Server: {app.config['MAIL_SERVER']}
- Port: {app.config['MAIL_PORT']}
- TLS: {app.config['MAIL_USE_TLS']}
- Username: {app.config['MAIL_USERNAME']}

If you received this email, your email configuration is working correctly!

Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Send the email
        mail.send(msg)
        
        return jsonify({
            'status': 'success',
            'message': f'Test email sent successfully to {app.config["MAIL_USERNAME"]}',
            'config': {
                'server': app.config['MAIL_SERVER'],
                'port': app.config['MAIL_PORT'],
                'tls': app.config['MAIL_USE_TLS'],
                'username': app.config['MAIL_USERNAME']
            }
        }), 200
        
    except Exception as e:
        print(f"Error sending test email: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to send test email: {str(e)}',
            'config': {
                'server': app.config['MAIL_SERVER'],
                'port': app.config['MAIL_PORT'],
                'tls': app.config['MAIL_USE_TLS'],
                'username': app.config['MAIL_USERNAME']
            }
        }), 500

@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password form"""
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        email = form.email.data
        user = AdminUser.query.filter_by(email=email, is_active=True).first()
        
        if user:
            # Generate reset token
            token = generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Save token to database
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            db.session.add(reset_token)
            db.session.commit()
            
            # Generate reset URL
            reset_url = url_for('reset_password', token=token, _external=True)
            
            # Send email
            if send_password_reset_email(user, reset_url):
                flash('Password reset instructions have been sent to your email.', 'success')
            else:
                flash('Failed to send password reset email. Please try again.', 'error')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('admin_login'))
    
    return render_template('admin_forgot_password.html', form=form)

@app.route('/admin/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset form"""
    # Find valid token
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_token or not reset_token.is_valid():
        flash('Invalid or expired password reset link.', 'error')
        return redirect(url_for('admin_login'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        # Update user password
        user = AdminUser.query.get(reset_token.user_id)
        user.password_hash = generate_password_hash(form.password.data)
        
        # Mark token as used
        reset_token.used = True
        
        db.session.commit()
        
        flash('Your password has been successfully reset. You can now login with your new password.', 'success')
        return redirect(url_for('admin_login'))
    
    return render_template('admin_reset_password.html', form=form, token=token)

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
            flash('Invalid credentials', 'error')
    
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



@app.route('/admin/analytics-dashboard')
def analytics_dashboard():
    """Advanced analytics dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin_analytics_dashboard.html')

@app.route('/admin/test-session')
def test_admin_session():
    """Test route to check admin session"""
    return jsonify({
        'admin_logged_in': session.get('admin_logged_in', False),
        'session_data': dict(session)
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)