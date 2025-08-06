# 📧 Email Setup Guide for Kaboy Agrovet Admin

This guide will help you set up email functionality for your Flask-Admin login system, including password reset capabilities.

## ✅ What's Already Implemented

Your Flask application already has:

1. **✅ Flask-Mail installed** - Version 0.10.0 is in requirements.txt
2. **✅ Email configuration** - Already configured in app.py
3. **✅ Test email route** - `/admin/test-email` endpoint
4. **✅ Test email page** - `/admin/test-email-page` with UI
5. **✅ Email functions** - For order notifications and low stock alerts

## 🔧 Step-by-Step Setup

### Step 1: Create .env File

Create a `.env` file in your project root with the following content:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_SECRET_KEY=your-super-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///instance/kaboy_agrovet.db

# Admin Configuration
ADMIN_PASSWORD_HASH=your-admin-password-hash-here

# Email Configuration for Flask-Mail
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=static/uploads
```

### Step 2: Configure Gmail (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this password in your `.env` file

### Step 3: Test Email Configuration

1. **Start your Flask application**:
   ```bash
   python app.py
   ```

2. **Login to admin dashboard**:
   - Go to http://127.0.0.1:5000/admin-login
   - Login with admin/admin123

3. **Test email functionality**:
   - Click the "📧 Test Email" button in the admin dashboard
   - Or go directly to http://127.0.0.1:5000/admin/test-email-page
   - Click "Send Test Email"
   - Check your email inbox

## 🔍 Troubleshooting

### Common Issues:

1. **"Email not configured" error**:
   - Make sure your `.env` file exists and has the correct values
   - Restart your Flask application after creating the `.env` file

2. **"Authentication failed" error**:
   - Check your Gmail username and app password
   - Make sure 2FA is enabled and you're using an app password, not your regular password

3. **"Connection refused" error**:
   - Check your firewall settings
   - Verify the SMTP server and port are correct
   - Try using port 465 with SSL instead of 587 with TLS

### Alternative Email Providers:

**Outlook/Hotmail**:
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

**Yahoo Mail**:
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

## 🚀 Next Steps

Once email is working, you can implement:

1. **Password Reset Functionality**:
   - Add "Forgot Password" link to login page
   - Create password reset tokens
   - Send reset emails with secure links

2. **Enhanced Notifications**:
   - Customer order confirmations
   - Shipping updates
   - Marketing emails

3. **Email Templates**:
   - Professional HTML email templates
   - Branded email signatures
   - Multi-language support

## 📞 Support

If you encounter issues:

1. Check the Flask application logs for error messages
2. Verify your email provider's SMTP settings
3. Test with a different email provider
4. Ensure your `.env` file is in the correct location

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use app passwords instead of regular passwords
- Consider using environment variables in production
- Regularly rotate your email credentials

---

**Kaboy Agrovet** - Your Trusted Agri-Partner in Nchiru 