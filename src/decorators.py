from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from models import User, db

def admin_required():
    """Decorator to require admin role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != 'admin':
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def role_required(required_role):
    """Decorator to require specific role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role != required_role and user_role != 'admin':
                return jsonify({"error": f"{required_role.capitalize()} access required"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def active_user_required():
    """Decorator to ensure user is active"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user or not user.is_active:
                return jsonify({"error": "Account is inactive"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper