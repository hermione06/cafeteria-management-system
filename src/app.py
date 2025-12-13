import os
from flask import Flask, render_template, session, redirect, url_for
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from src.models import db
from src.config import config
from src.routes import register_routes


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    # app.secret_key = 'your-secret-key-here'  # Change in production
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name not in config:
        config_name = 'default'
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    CORS(app)

    with app.app_context():
        from src.models import User, Order, OrderItem, MenuItem, Announcement   # import all models
        db.create_all()
        print("✅ Database tables created/verified")
    
    # Register all routes
    register_routes(app)
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"error": "Invalid token", "message": str(error)}, 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return {"error": "Missing authorization token", "message": str(error)}, 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"error": "Token has expired", "message": "Please refresh your token"}, 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"error": "Token has been revoked"}, 401
    
    # Health check
    @app.route('/health')
    def health():
        return {"status": "healthy", "environment": config_name}, 200
    
    # ==================== HTML TEMPLATE ROUTES ====================
    
    @app.route('/')
    def index():
        """Home page"""
        return render_template('index.html')
    
    @app.route('/login')
    def login_page():
        """Login page"""
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        """Registration page"""
        return render_template('register.html')
    
    @app.route('/menu')
    def menu_page():
        """Menu page"""
        return render_template('menu.html')
    
    @app.route('/dashboard')
    def dashboard():
        """User dashboard"""
        return render_template('dashboard.html')
    
    @app.route('/orders')
    def orders_page():
        """Orders page"""
        return render_template('orders.html')
    
    @app.route('/orders/<int:order_id>')
    def order_detail(order_id):
        """Order detail page"""
        return render_template('orders.html')
    
    @app.route('/profile')
    def profile_page():
        """User profile page"""
        return render_template('profile.html')
    
    @app.route('/admin/dashboard')
    def admin_dashboard():
        """Admin dashboard"""
        return render_template('admin_dashboard.html')
    
    @app.route('/staff/dashboard')
    def staff_dashboard():
        """Staff dashboard"""
        return render_template('staff_dashboard.html')
    
    @app.route('/forgot-password')
    def forgot_password_page():
        """Forgot password page"""
        return render_template('forgot_password.html')
    
    return app



if __name__ == '__main__':
    app = create_app()

    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )