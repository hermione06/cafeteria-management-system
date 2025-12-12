"""
Centralized route registration
"""
from .auth_routes import auth_bp
from .user_routes import user_bp
from .menu_routes import menu_bp
from .order_routes import order_bp
from .announcement_routes import announcement_bp


def register_routes(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(announcement_bp, url_prefix='/api/announcements')