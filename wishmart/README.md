# E-commerce Store

A modern, feature-rich e-commerce platform built with Django.

## Features

- **User Authentication**: Registration, login, logout
- **Product Management**: Categories, products with images, stock management
- **Shopping Cart**: Add/remove items, quantity management
- **Order Processing**: Checkout, order history, order details
- **Product Reviews**: User ratings and comments
- **Search & Filtering**: Product search and category filtering
- **Email Notifications**: Order confirmations and welcome emails
- **Payment Integration**: Stripe payment processing (ready for integration)
- **Responsive Design**: Mobile-friendly interface
- **Security**: CSRF protection, secure headers, environment variables

## Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with Bootstrap-like components
- **Payment**: Stripe (configured but not fully integrated)
- **Email**: SMTP (Gmail/other providers)
- **Deployment**: Gunicorn, Whitenoise

## Installation

### Prerequisites

- Python 3.8+
- pip
- virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd e-commerce/wishmart
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
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your settings
   # At minimum, set a new SECRET_KEY
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (for production, use PostgreSQL)
DATABASE_URL=sqlite:///db.sqlite3

# Email Settings (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Settings (for production)
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_SECRET_KEY=your-stripe-secret-key

# Static Files
STATIC_ROOT=staticfiles/
```

## Project Structure

```
wishmart/
├── ecommerce/              # Django project settings
│   ├── settings.py         # Main settings file
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── store/                  # Main app
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # App URL patterns
│   ├── admin.py           # Admin interface
│   ├── cart.py            # Shopping cart logic
│   ├── payments.py        # Payment processing
│   ├── notifications.py   # Email notifications
│   └── templates/         # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User-uploaded files
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
└── README.md              # This file
```

## Key Features Explained

### Shopping Cart
- Session-based cart system
- Add/remove items
- Quantity management
- Stock validation

### Product Management
- Categories and products
- Image uploads
- Stock tracking
- Product reviews and ratings

### Order Processing
- Checkout form validation
- Order creation and tracking
- Email confirmations
- Order history

### Security Features
- CSRF protection
- Secure headers
- Environment variable configuration
- Input validation
- SQL injection prevention

## Production Deployment

### Recommended Setup

1. **Use PostgreSQL** instead of SQLite
2. **Set DEBUG=False** in production
3. **Configure proper ALLOWED_HOSTS**
4. **Use HTTPS** with SSL certificates
5. **Set up proper email configuration**
6. **Configure Stripe** for payments
7. **Use a production WSGI server** (Gunicorn)
8. **Set up static file serving** (Whitenoise/nginx)

### Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set secure `SECRET_KEY`
- [ ] Configure database (PostgreSQL)
- [ ] Set up email backend
- [ ] Configure static files
- [ ] Set up SSL/HTTPS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Test payment integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository. 