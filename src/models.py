from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash
import secrets
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import secrets

db = SQLAlchemy()

class User(db.Model):
    """User model for cafeteria staff and customers"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # user, admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)    
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        """Generate a unique verification token"""
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token
    
    def generate_reset_token(self):
        """Generate a unique password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)  # ✅ timezone-aware UTC
        return self.reset_token
    
    def verify_email(self):
        """Mark user's email as verified"""
        self.is_verified = True
        self.verification_token = None
    
    def update_last_login(self):
         """Update the last login timestamp"""
         self.last_login = datetime.now(timezone.utc)
    
    def to_dict(self, include_sensitive=False):
        """Convert user object to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['verification_token'] = self.verification_token
            data['reset_token'] = self.reset_token
        
        return data
    
    @staticmethod
    def validate_role(role):
        """Validate user role"""
        valid_roles = ['user', 'admin']
        return role in valid_roles
    

# Menu Item and Category Models


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    items = db.relationship("MenuItem", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)

    picture_url = db.Column(db.String(255), nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    stock = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "available": self.available,
            "picture_url": self.picture_url,
            "category": self.category.name if self.category else None,
            "stock": self.stock,
        }
