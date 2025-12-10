from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import secrets

db = SQLAlchemy()

# ============================
# USER MODEL
# ============================

class User(db.Model):
    """User model for cafeteria staff and customers"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)

    def set_password(self, password):
        hashed = generate_password_hash(password)
        if isinstance(hashed, bytes):
            hashed = hashed.decode('utf-8')
        self.password_hash = hashed

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self):
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        return self.reset_token

    def verify_email(self):
        self.is_verified = True
        self.verification_token = None

    def update_last_login(self):
        self.last_login = datetime.now(timezone.utc)

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
        if include_sensitive:
            data['verification_token'] = self.verification_token
            data['reset_token'] = self.reset_token
        return data

    @staticmethod
    def validate_role(role):
        return role in ['user', 'admin']


# ============================
# CATEGORY MODEL
# ============================

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    items = db.relationship("MenuItem", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


# ============================
# MENU ITEM MODEL
# ============================

class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)
    picture_url = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, default=0)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    def __init__(self, *args, **kwargs):
        category_str = kwargs.pop("category", None)
        super().__init__(*args, **kwargs)

        if category_str:
            cat = Category.query.filter_by(name=category_str).first()
            if not cat:
                cat = Category(name=category_str)
                db.session.add(cat)
                db.session.flush()  
            self.category_id = cat.id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "available": self.available,
            "picture_url": self.picture_url,
            "category": self.category.name if self.category else None,
            "stock": self.stock,
        }
        """Validate user role"""
        valid_roles = ['user', 'admin']
        return role in valid_roles
    
class Order(db.Model):
    """Order model for cafeteria orders"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    is_paid = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(),
                           onupdate=func.now(), nullable=False)

    # Relationship to OrderItem
    items = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Order {self.id} | User {self.user_id}>"

    @staticmethod
    def validate_status(status):
        return status in ['pending', 'preparing', 'ready', 'completed', 'cancelled']

    def calculate_total(self):
        """Calculate total using related OrderItem rows."""
        return sum(item.quantity * item.menu_item.price for item in self.items)

    def to_dict(self, include_items=True, include_user=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "is_paid": self.is_paid,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "total_price": self.calculate_total()
        }

        if include_items:
            data["items"] = [item.to_dict(include_menu=True) for item in self.items]

        if include_user:
            data["user"] = self.user.to_dict()

        return data


class OrderItem(db.Model):
    """Join table: items inside an order"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False, index=True)

    # Relationship to menu item
    menu_item = db.relationship('MenuItem', backref=db.backref('order_items', lazy=True))

    quantity = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<OrderItem Order {self.order_id} | MenuItem {self.menu_item_id}>"

    def to_dict(self, include_menu=False):
        data = {
            "id": self.id,
            "order_id": self.order_id,
            "menu_item_id": self.menu_item_id,
            "quantity": self.quantity
        }

        if include_menu:
            data["menu_item"] = self.menu_item.to_dict()

        return data
