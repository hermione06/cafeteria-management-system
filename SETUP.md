# CafeHub - Complete Setup Guide

## 📁 Project Structure

```
cafeteria-management-system/
├── app.py                      # Main application entry point
├── config.py                   # Configuration management
├── models.py                   # Database models
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Your environment variables (create this)
├── routes/
│   ├── __init__.py            # Route registration
│   ├── auth_routes.py         # Authentication endpoints
│   ├── user_routes.py         # User management
│   ├── menu_routes.py         # Menu management
│   ├── order_routes.py        # Order management
│   └── announcement_routes.py # Announcements
├── utils/
│   ├── decorators.py          # Authorization decorators
│   └── pagination.py          # Pagination helper
├── templates/
│   ├── base.html              # Base template with navbar
│   ├── index.html             # Home page
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── menu.html              # Menu page with cart
│   ├── dashboard.html         # User dashboard
│   ├── orders.html            # Orders page
│   ├── profile.html           # User profile
│   └── admin_dashboard.html   # Admin dashboard
├── static/                    # Static files (create if needed)
│   ├── css/
│   ├── js/
│   └── images/
└── instance/
    └── cafeteria_dev.db       # SQLite database (auto-created)
```

## 🚀 Step-by-Step Setup

### 1. Prerequisites

Make sure you have installed:
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

Check your Python version:
```bash
python --version
# or
python3 --version
```

### 2. Create Project Directory

```bash
mkdir cafeteria-management-system
cd cafeteria-management-system
```

### 3. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 4. Install Dependencies

Create `requirements.txt` with the following content:
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-JWT-Extended==4.6.0
Flask-Bcrypt==1.0.1
Flask-CORS==4.0.0
email-validator==2.1.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

Then install:
```bash
pip install -r requirements.txt
```

### 5. Create Directory Structure

```bash
# Create folders
mkdir routes utils templates static instance

# Create routes folder files
touch routes/__init__.py
touch routes/auth_routes.py
touch routes/user_routes.py
touch routes/menu_routes.py
touch routes/order_routes.py
touch routes/announcement_routes.py

# Create utils folder files
touch utils/decorators.py
touch utils/pagination.py

# Create main files
touch app.py
touch config.py
touch models.py
touch .env
```

### 6. Setup Environment Variables

Create `.env` file in the root directory:
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# Database Configuration
DATABASE_URL=sqlite:///instance/cafeteria_dev.db

# Server Configuration
PORT=5000

# Email Configuration (optional for now)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@cafeteria.com
```

**Important:** Generate strong secret keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Use the output for SECRET_KEY and JWT_SECRET_KEY.

### 7. Copy All Code Files

Copy all the Python and HTML code I provided into their respective files:

- **Backend Files:**
  - `app.py` - Main application
  - `config.py` - Configuration
  - `models.py` - Database models
  - `routes/` - All route files
  - `utils/` - Utility files

- **Frontend Files (templates/):**
  - `base.html` - Base template
  - `index.html` - Home page
  - `login.html` - Login page
  - `register.html` - Registration page
  - `menu.html` - Menu page
  - `dashboard.html` - User dashboard
  - `orders.html` - Orders page
  - `profile.html` - User profile
  - `admin_dashboard.html` - Admin dashboard

### 8. Initialize Database

```bash
# Create instance directory if it doesn't exist
mkdir -p instance

# Run the application (it will create database automatically)
python app.py
```

You should see:
```
✅ Database tables created/verified
 * Running on http://0.0.0.0:5000
```

### 9. Create Admin User (Optional)

Open Python shell while app is running:
```bash
# In a new terminal, activate venv first
python
```

Then in Python:
```python
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    # Create admin user
    admin = User(
        username='admin',
        email='admin@cafehub.com',
        role='admin'
    )
    admin.set_password('admin123')
    admin.is_verified = True  # Skip email verification
    admin.is_active = True
    
    db.session.add(admin)
    db.session.commit()
    
    print("✅ Admin user created!")
    print("Username: admin")
    print("Password: admin123")

exit()
```

### 10. Create Sample Menu Items

```python
from app import create_app
from models import db, MenuItem

app = create_app()
with app.app_context():
    items = [
        MenuItem(name='Coffee', description='Fresh brewed coffee', price=2.50, category='beverages', is_available=True),
        MenuItem(name='Cappuccino', description='Espresso with steamed milk', price=3.50, category='beverages', is_available=True),
        MenuItem(name='Burger', description='Classic beef burger', price=8.99, category='food', is_available=True),
        MenuItem(name='Pizza Slice', description='Cheese pizza', price=4.50, category='food', is_available=True),
        MenuItem(name='Caesar Salad', description='Fresh romaine lettuce', price=6.99, category='food', is_available=True),
        MenuItem(name='Chips', description='Potato chips', price=1.99, category='snacks', is_available=True),
        MenuItem(name='Cookie', description='Chocolate chip cookie', price=2.50, category='desserts', is_available=True),
    ]
    
    for item in items:
        db.session.add(item)
    
    db.session.commit()
    print(f"✅ Created {len(items)} menu items!")

exit()
```

## 🎯 Running the Application

### Development Mode

```bash
# Make sure virtual environment is activated
python app.py
```

The application will be available at:
- **Frontend:** http://localhost:5000
- **API:** http://localhost:5000/api

### Production Mode

```bash
# Set environment
export FLASK_ENV=production  # Linux/macOS
set FLASK_ENV=production     # Windows

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📝 Testing the Application

### 1. Register a New User
1. Go to http://localhost:5000
2. Click "Sign Up"
3. Fill in registration form
4. Note: Email verification is simulated (check terminal for token)

### 2. Login
1. Go to http://localhost:5000/login
2. Use your credentials (or admin/admin123)
3. You'll be redirected to dashboard

### 3. Browse Menu
1. Click "Menu" in navigation
2. Search and filter items
3. Add items to cart
4. Proceed to checkout

### 4. View Orders
1. Go to "Orders" page
2. Track order status
3. View order details

### 5. Admin Dashboard (if admin)
1. Login as admin
2. Go to "Admin" in navigation
3. Manage users, menu, orders, announcements

## 🔧 Common Issues & Solutions

### Issue: ModuleNotFoundError
**Solution:** Make sure virtual environment is activated and all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Database errors
**Solution:** Delete the database and recreate:
```bash
rm instance/cafeteria_dev.db
python app.py
```

### Issue: Port already in use
**Solution:** Change port in .env file or kill the process:
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process or change PORT in .env
```

### Issue: CORS errors
**Solution:** CORS is already configured in app.py. If issues persist, check browser console.

### Issue: JWT token errors
**Solution:** Clear browser localStorage:
```javascript
// In browser console
localStorage.clear();
```

## 📱 Features Overview

### User Features:
- ✅ User registration with email verification
- ✅ Login/Logout with JWT authentication
- ✅ Browse menu with search and filters
- ✅ Add items to cart
- ✅ Place orders
- ✅ Track order status
- ✅ View order history
- ✅ Update profile
- ✅ Change password

### Staff Features (if role is 'staff'):
- ✅ All user features
- ✅ Manage menu item availability
- ✅ Update order status
- ✅ Mark orders as paid

### Admin Features:
- ✅ All staff features
- ✅ User management (view, create, update, delete)
- ✅ Full menu management (CRUD)
- ✅ Order management
- ✅ Create announcements
- ✅ View statistics and reports

## 🔐 Security Notes

1. **Change default secrets** in `.env` file
2. **Never commit** `.env` file to git (add to .gitignore)
3. **In production:**
   - Use PostgreSQL instead of SQLite
   - Enable HTTPS
   - Set secure cookie flags
   - Implement rate limiting
   - Add token blacklisting for logout

## 📚 API Endpoints

All API endpoints are prefixed with `/api`:

### Authentication
- POST `/api/auth/register` - Register user
- POST `/api/auth/login` - Login
- POST `/api/auth/logout` - Logout
- POST `/api/auth/refresh` - Refresh token
- GET `/api/auth/me` - Get current user

### Menu
- GET `/api/menu` - Get all menu items
- GET `/api/menu/<id>` - Get specific item
- POST `/api/menu` - Create item (admin)
- PUT `/api/menu/<id>` - Update item (staff/admin)
- DELETE `/api/menu/<id>` - Delete item (admin)

### Orders
- GET `/api/orders` - Get orders
- POST `/api/orders` - Create order
- GET `/api/orders/<id>` - Get order details
- PATCH `/api/orders/<id>/status` - Update status (staff/admin)
- DELETE `/api/orders/<id>` - Cancel order

Full API documentation in README.md

## 🎨 Customization

### Change Colors
Edit `templates/base.html` and update Tailwind config:
```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#your-color',
                secondary: '#your-color',
                accent: '#your-color',
            }
        }
    }
}
```

### Add Logo
1. Save logo image in `static/images/logo.png`
2. Update navigation in `base.html`

### Modify Menu Categories
Edit `models.py` in `MenuItem.validate_category()` method

## 🚀 Deployment

### Deploy to Heroku
1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Create `runtime.txt`:
```
python-3.11.0
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Deploy to Railway/Render
- Use the same Procfile
- Set environment variables in platform dashboard
- Connect your git repository

## 📞 Support

If you encounter any issues:
1. Check terminal/console for error messages
2. Review this guide
3. Check browser console for frontend errors
4. Verify all files are in correct locations

## 🎉 You're Done!

Your cafeteria management system is now ready to use! 

Start the server and visit: **http://localhost:5000**

Happy coding! 🚀☕