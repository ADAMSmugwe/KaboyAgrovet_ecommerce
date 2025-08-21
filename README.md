<<<<<<< HEAD
# 🐄 Kaboy Agrovet eCommerce System

An all-in-one eCommerce and inventory management platform built for **Kaboy Agrovet** in **Kianjai, Meru County, Kenya**. The platform allows customers to place orders for agricultural products, integrates MPesa payments, tracks inventory in real-time, and provides an admin dashboard for sales and order management.

---



---

## 🚀 Features

- 🛒 Clean, responsive eCommerce UI
- 📦 Smart inventory tracking
- 📱 **MPesa API** payment integration
- 📊 Admin dashboard for managing orders, inventory & sales
- 📩 Automatic email confirmations after payment
- 🔐 Admin login system
- 📍 Location map for Kaboy Agrovet (Google Maps API)
- 🎯 Smooth scrolling, animations, hover effects

---

## 🧠 Tech Stack

| Frontend         | Backend         | Payment       | DB           | Deployment |
|------------------|------------------|---------------|--------------|------------|
| HTML, CSS, JS     | Flask (Python)   | MPesa API     | SQLite       | Render     |
| Bootstrap/Tailwind| SQLAlchemy       | Email (SMTP)  |               |            |

---

## 🔧 Installation

```bash
git clone https://github.com/ADAMSmugwe/kaboyAgrovet_ecommerce.git
cd kaboy-agrovet
pip install -r requirements.txt
python app.py
=======
# Kaboy Agrovet E-Commerce Platform

A comprehensive e-commerce solution for Kaboy Agrovet, an agricultural products store in Nchiru, Kenya.

## 🌟 Features

### Customer-Facing Features
- **Product Catalog**: Browse and search agricultural products
- **Shopping Cart**: Add items and manage quantities
- **Order Management**: Place orders with delivery details
- **Responsive Design**: Mobile-friendly interface
- **Product Categories**: Fertilizers, Pesticides, Seeds, Feed, etc.
- **Contact Form**: Customer inquiries and support
- **Testimonials**: Customer reviews and feedback
- **FAQ Section**: Common questions and answers

### Admin Features
- **Flask-Admin Interface**: Complete CRUD operations for all models
- **Dashboard Analytics**: Sales trends, stock levels, order statistics
- **Manual Sales Entry**: POS system for walk-in customers
- **Stock Management**: Real-time inventory tracking
- **Order Processing**: View and manage customer orders
- **Email Notifications**: Order alerts and low stock warnings
- **File Upload**: Product image management

### 🆕 NEW: Purchase Management System
- **Supplier Management**: Add and manage suppliers
- **Purchase Orders**: Create and track purchase orders
- **Stock Receiving**: Receive stock from suppliers and update inventory
- **Purchase History**: Complete purchase order tracking
- **Supplier Analytics**: Purchase patterns and supplier performance

### 🆕 NEW: Accounting & Financial Management
- **Expense Tracking**: Record and categorize business expenses
- **Profit & Loss Reports**: Automated P&L calculations
- **Financial Analytics**: Revenue, expenses, and profit analysis
- **Expense Categories**: Organized expense management
- **Financial Reports**: Generate various financial reports

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (with SQLAlchemy ORM)
- **Admin Interface**: Flask-Admin
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Email**: Flask-Mail
- **File Upload**: Werkzeug

## 📋 Prerequisites

- Python 3.9+
- pip (Python package manager)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd KaboyAgrovet_ecommerce
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   FLASK_SECRET_KEY=your-super-secret-key-here
   DATABASE_URL=sqlite:///instance/kaboy_agrovet.db
   ADMIN_PASSWORD_HASH=your-admin-password-hash-here
   
   # Optional: Email configuration
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

5. **Initialize database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## 🌐 Access Points

- **Main Website**: http://127.0.0.1:5000
- **Admin Login**: http://127.0.0.1:5000/admin-login
- **Admin Dashboard**: http://127.0.0.1:5000/admin/
- **Custom Dashboard**: http://127.0.0.1:5000/admin-dashboard

## 🔐 Default Admin Credentials

- **Username**: admin
- **Password**: admin123

## 📊 Database Models

### Core Models
- **Product**: Main product information
- **ProductVariant**: Specific product variants with pricing and stock
- **Order**: Customer orders from website
- **OrderItem**: Individual items in orders
- **OfflineSale**: Manual sales from store
- **OfflineSaleItem**: Items in offline sales

### 🆕 Purchase Management Models
- **Supplier**: Supplier information and contact details
- **Purchase**: Purchase orders from suppliers
- **PurchaseItem**: Individual items in purchase orders

### 🆕 Accounting Models
- **Expense**: Business expense tracking
- **FinancialReport**: Generated financial reports

### Content Models
- **Testimonial**: Customer reviews
- **FAQ**: Frequently asked questions
- **ContactMessage**: Customer contact form submissions

## 🔧 API Endpoints

### Public APIs
- `GET /api/products` - Product catalog
- `GET /api/testimonials` - Approved testimonials
- `GET /api/faqs` - FAQ list
- `POST /api/contact` - Contact form submission
- `POST /api/submit-full-order` - Order submission

### Admin APIs
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/sales-trends` - Sales trend data
- `GET /api/dashboard/stock-levels` - Stock level data
- `GET /api/dashboard/recent-online-orders` - Recent orders
- `GET /api/dashboard/recent-offline-sales` - Recent sales
- `POST /api/manual-sale` - Manual sale entry
- `POST /api/restock-product` - Stock management

### 🆕 Purchase Management APIs
- `GET /api/suppliers` - Get all active suppliers
- `GET /api/purchases` - Get all purchase orders
- `POST /api/purchase/create` - Create new purchase order
- `POST /api/purchase/receive-stock` - Receive stock from purchase

### 🆕 Accounting APIs
- `POST /api/expense/create` - Create new expense record
- `GET /api/accounting/profit-loss` - Calculate P&L for period
- `GET /api/accounting/expenses-by-category` - Get expenses by category

## 📁 Project Structure

```
KaboyAgrovet_ecommerce/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── instance/             # Database files
├── migrations/           # Database migrations
├── static/              # Static files
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   ├── images/         # Product images
│   └── uploads/        # Uploaded files
└── templates/          # HTML templates
    ├── admin/          # Admin templates
    ├── emails/         # Email templates
    ├── index.html      # Main page
    ├── cart.html       # Shopping cart
    └── admin_dashboard.html # Custom dashboard
```

## 🔄 Stock Management

The system automatically:
- **Tracks stock levels** for all product variants
- **Prevents overselling** by checking stock before order completion
- **Updates inventory** when orders are placed or manual sales are made
- **Sends low stock alerts** when inventory falls below 10 units
- **Provides restocking API** for admin use
- **🆕 Receives stock** from purchase orders automatically

## 🆕 Purchase Management Workflow

1. **Add Suppliers**: Create supplier records with contact information
2. **Create Purchase Orders**: Generate purchase orders with items and costs
3. **Receive Stock**: Mark purchases as received to update inventory
4. **Track Payments**: Monitor payment status for purchases
5. **Analyze Performance**: View purchase analytics and supplier performance

## 🆕 Accounting Features

- **Expense Tracking**: Record business expenses by category
- **Profit & Loss**: Automated calculation of revenue, expenses, and profit
- **Financial Reports**: Generate various financial reports
- **Cost Analysis**: Track cost of goods sold and operating expenses
- **Profit Margins**: Calculate and monitor profit margins

## 📧 Email Notifications

Configure email settings in `.env` to receive:
- **Order notifications** when new orders are placed
- **Low stock alerts** when inventory is running low
- **🆕 Purchase confirmations** when purchase orders are created
- **🆕 Financial reports** when generated

## 🛡️ Security Features

- **Admin authentication** with session management
- **CSRF protection** on forms
- **Input validation** on all API endpoints
- **File upload restrictions** for images only
- **SQL injection prevention** through SQLAlchemy ORM

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production
For production deployment, consider:
- Using a production WSGI server (Gunicorn, uWSGI)
- Setting up a proper database (PostgreSQL, MySQL)
- Configuring HTTPS
- Setting up proper logging
- Using environment-specific configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support or questions, contact:
- **Store**: Kaboy Agrovet, Nchiru, Kenya
- **Location**: Next to Meru University of Science and Technology

## 📄 License

This project is proprietary software for Kaboy Agrovet.

---

**Kaboy Agrovet** - Your Trusted Agri-Partner in Nchiru 
>>>>>>> main
