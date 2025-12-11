from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy import func, Index
import secrets

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user', index=True)
    
    # Status fields
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Token fields
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), 
                          onupdate=func.now(), nullable=False)
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Relationships
    orders = db.relationship('Order', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    
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
        """Generate a unique password reset token with expiry"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
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
        valid_roles = ['user', 'admin', 'staff']
        return role in valid_roles


class MenuItem(db.Model):
    """Menu item model"""
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    image_url = db.Column(db.String(255), nullable=True)
    
    # Inventory
    is_available = db.Column(db.Boolean, default=True, nullable=False, index=True)
    stock_quantity = db.Column(db.Integer, default=0, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(),
                          onupdate=func.now(), nullable=False)
    
    # Relationships
    order_items = db.relationship('OrderItem', back_populates='menu_item', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        Index('idx_menu_category_available', 'category', 'is_available'),
    )
    
    def __repr__(self):
        return f'<MenuItem {self.name}>'
    
    def to_dict(self):
        """Convert menu item to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'stock_quantity': self.stock_quantity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def validate_category(category):
        """Validate menu item category"""
        valid_categories = ['beverages', 'food', 'snacks', 'desserts']
        return category.lower() in valid_categories


class Order(db.Model):
    """Order model"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                       nullable=False, index=True)
    
    # Order details
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    is_paid = db.Column(db.Boolean, default=False, nullable=False, index=True)
    payment_method = db.Column(db.String(50), nullable=True)
    
    # Notes
    special_instructions = db.Column(db.Text, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(),
                          onupdate=func.now(), nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', 
                           cascade='all, delete-orphan', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        Index('idx_order_user_status', 'user_id', 'status'),
        Index('idx_order_created', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Order {self.id} | User {self.user_id} | Status {self.status}>'
    
    @staticmethod
    def validate_status(status):
        """Validate order status"""
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled']
        return status in valid_statuses
    
    def calculate_total(self):
        """Calculate order total"""
        return sum(item.subtotal for item in self.items)
    
    def to_dict(self, include_items=True, include_user=False):
        """Convert order to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'is_paid': self.is_paid,
            'payment_method': self.payment_method,
            'special_instructions': self.special_instructions,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_price': self.calculate_total()
        }
        
        if include_items:
            data['items'] = [item.to_dict(include_menu=True) for item in self.items]
        
        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email
            }
        
        return data


class OrderItem(db.Model):
    """Order item model - junction table with additional data"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), 
                        nullable=False, index=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', ondelete='RESTRICT'), 
                            nullable=False, index=True)
    
    # Order item details
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)  # Price at time of order
    
    # Relationships
    order = db.relationship('Order', back_populates='items')
    menu_item = db.relationship('MenuItem', back_populates='order_items')
    
    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} MenuItem:{self.menu_item_id}>'
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.unit_price
    
    def to_dict(self, include_menu=False):
        """Convert order item to dictionary"""
        data = {
            'id': self.id,
            'order_id': self.order_id,
            'menu_item_id': self.menu_item_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.subtotal
        }
        
        if include_menu and self.menu_item:
            data['menu_item'] = self.menu_item.to_dict()
        
        return data


class Announcement(db.Model):
    """Announcement model for cafeteria notifications"""
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal', nullable=False)  # low, normal, high
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Creator
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(),
                          onupdate=func.now(), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f'<Announcement {self.title}>'
    
    def to_dict(self):
        """Convert announcement to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }