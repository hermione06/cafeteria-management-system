"""
Tests for database models.
Testing model creation, validation, relationships, and methods.
"""
import pytest
from datetime import datetime, timedelta, timezone
from models import User, MenuItem, Order, OrderItem, Announcement


# ==================== User Model Tests ====================

class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self, app):
        """Test creating a user with required fields."""
        with app.app_context():
            user = User(
                username='newuser',
                email='new@example.com',
                role='user'
            )
            user.set_password('password123')
            
            assert user.username == 'newuser'
            assert user.email == 'new@example.com'
            assert user.role == 'user'
            assert user.is_active is True
            assert user.is_verified is False
            assert user.password_hash is not None
    
    def test_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('MySecretPassword123')
            
            assert user.password_hash != 'MySecretPassword123'
            assert user.check_password('MySecretPassword123') is True
            assert user.check_password('WrongPassword') is False
    
    def test_verification_token_generation(self, app):
        """Test email verification token generation."""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            token = user.generate_verification_token()
            
            assert token is not None
            assert len(token) > 20
            assert user.verification_token == token
    
    def test_reset_token_generation(self, app):
        """Test password reset token generation."""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            token = user.generate_reset_token()
            
            assert token is not None
            assert user.reset_token == token
            assert user.reset_token_expiry is not None
            assert user.reset_token_expiry > datetime.now(timezone.utc)
    
    def test_verify_email(self, app):
        """Test email verification."""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.generate_verification_token()
            
            assert user.is_verified is False
            
            user.verify_email()
            
            assert user.is_verified is True
            assert user.verification_token is None
    
    def test_update_last_login(self, app):
        """Test updating last login timestamp."""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            
            assert user.last_login is None
            
            user.update_last_login()
            
            assert user.last_login is not None
            assert isinstance(user.last_login, datetime)
    
    def test_user_to_dict(self, app):
        """Test user serialization to dictionary."""
        with app.app_context():
            user = User(username='test', email='test@example.com', role='user')
            user.set_password('password')
            
            user_dict = user.to_dict()
            
            assert user_dict['username'] == 'test'
            assert user_dict['email'] == 'test@example.com'
            assert user_dict['role'] == 'user'
            assert 'password_hash' not in user_dict
            assert 'created_at' in user_dict
            assert 'verification_token' not in user_dict
    
    def test_user_to_dict_include_sensitive(self, app):
        """Test user serialization with sensitive data."""
        with app.app_context():
            user = User(username='test', email='test@example.com')
            user.generate_verification_token()
            
            user_dict = user.to_dict(include_sensitive=True)
            
            assert 'verification_token' in user_dict
            assert 'reset_token' in user_dict
    
    def test_validate_role_valid(self):
        """Test role validation with valid roles."""
        assert User.validate_role('user') is True
        assert User.validate_role('admin') is True
        assert User.validate_role('staff') is True
    
    def test_validate_role_invalid(self):
        """Test role validation with invalid roles."""
        assert User.validate_role('superuser') is False
        assert User.validate_role('guest') is False
        assert User.validate_role('') is False
    
    def test_user_relationships(self, app, user):
        """Test user-order relationship."""
        with app.app_context():
            order = Order(user_id=user.id, status='pending')
            from models import db
            db.session.add(order)
            db.session.commit()
            
            assert len(user.orders.all()) == 1
            assert user.orders.first().user_id == user.id


# ==================== MenuItem Model Tests ====================

class TestMenuItemModel:
    """Test MenuItem model functionality."""
    
    def test_menu_item_creation(self, app):
        """Test creating a menu item."""
        with app.app_context():
            item = MenuItem(
                name='Test Item',
                description='Test description',
                price=9.99,
                category='food',
                is_available=True
            )
            
            assert item.name == 'Test Item'
            assert item.price == 9.99
            assert item.category == 'food'
            assert item.is_available is True
    
    def test_menu_item_to_dict(self, app, menu_item):
        """Test menu item serialization."""
        with app.app_context():
            item_dict = menu_item.to_dict()
            
            assert item_dict['name'] == menu_item.name
            assert item_dict['price'] == menu_item.price
            assert item_dict['category'] == menu_item.category
            assert 'created_at' in item_dict
            assert 'updated_at' in item_dict
    
    def test_validate_category_valid(self):
        """Test category validation with valid categories."""
        assert MenuItem.validate_category('beverages') is True
        assert MenuItem.validate_category('food') is True
        assert MenuItem.validate_category('snacks') is True
        assert MenuItem.validate_category('desserts') is True
        assert MenuItem.validate_category('BEVERAGES') is True  # Case insensitive
    
    def test_validate_category_invalid(self):
        """Test category validation with invalid categories."""
        assert MenuItem.validate_category('invalid') is False
        assert MenuItem.validate_category('') is False
    
    def test_menu_item_stock_tracking(self, app):
        """Test stock quantity tracking."""
        with app.app_context():
            item = MenuItem(
                name='Test',
                price=5.0,
                category='food',
                stock_quantity=10
            )
            
            assert item.stock_quantity == 10
            
            item.stock_quantity = 0
            item.is_available = False
            
            assert item.stock_quantity == 0
            assert item.is_available is False


# ==================== Order Model Tests ====================

class TestOrderModel:
    """Test Order model functionality."""
    
    def test_order_creation(self, app, user):
        """Test creating an order."""
        with app.app_context():
            order = Order(user_id=user.id, status='pending')
            
            assert order.user_id == user.id
            assert order.status == 'pending'
            assert order.is_paid is False
    
    def test_validate_status_valid(self):
        """Test status validation with valid statuses."""
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled']
        for status in valid_statuses:
            assert Order.validate_status(status) is True
    
    def test_validate_status_invalid(self):
        """Test status validation with invalid statuses."""
        assert Order.validate_status('invalid') is False
        assert Order.validate_status('') is False
    
    def test_calculate_total(self, app, order):
        """Test order total calculation."""
        with app.app_context():
            total = order.calculate_total()
            
            # Coffee (2.50 * 2) + Burger (8.99 * 1) = 13.99
            assert total == pytest.approx(13.99, 0.01)
    
    def test_order_to_dict_basic(self, app, order):
        """Test order serialization without items."""
        with app.app_context():
            order_dict = order.to_dict(include_items=False)
            
            assert order_dict['id'] == order.id
            assert order_dict['user_id'] == order.user_id
            assert order_dict['status'] == 'pending'
            assert 'items' not in order_dict
    
    def test_order_to_dict_with_items(self, app, order):
        """Test order serialization with items."""
        with app.app_context():
            order_dict = order.to_dict(include_items=True)
            
            assert 'items' in order_dict
            assert len(order_dict['items']) == 2
            assert order_dict['total_price'] == pytest.approx(13.99, 0.01)
    
    def test_order_to_dict_with_user(self, app, order):
        """Test order serialization with user info."""
        with app.app_context():
            order_dict = order.to_dict(include_user=True)
            
            assert 'user' in order_dict
            assert order_dict['user']['username'] == 'testuser'
    
    def test_order_relationships(self, app, order):
        """Test order relationships."""
        with app.app_context():
            assert order.user is not None
            assert order.user.username == 'testuser'
            assert len(list(order.items)) == 2


# ==================== OrderItem Model Tests ====================

class TestOrderItemModel:
    """Test OrderItem model functionality."""
    
    def test_order_item_creation(self, app, order, menu_item):
        """Test creating an order item."""
        with app.app_context():
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=3,
                unit_price=menu_item.price
            )
            
            assert order_item.quantity == 3
            assert order_item.unit_price == menu_item.price
    
    def test_subtotal_calculation(self, app, order, menu_item):
        """Test order item subtotal calculation."""
        with app.app_context():
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=3,
                unit_price=5.99
            )
            
            assert order_item.subtotal == pytest.approx(17.97, 0.01)
    
    def test_order_item_to_dict(self, app, order, menu_item):
        """Test order item serialization."""
        with app.app_context():
            from models import db
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=2,
                unit_price=5.99
            )
            db.session.add(order_item)
            db.session.commit()
            
            item_dict = order_item.to_dict(include_menu=True)
            
            assert item_dict['quantity'] == 2
            assert item_dict['unit_price'] == 5.99
            assert 'menu_item' in item_dict
            assert item_dict['menu_item']['name'] == menu_item.name


# ==================== Announcement Model Tests ====================

class TestAnnouncementModel:
    """Test Announcement model functionality."""
    
    def test_announcement_creation(self, app, admin_user):
        """Test creating an announcement."""
        with app.app_context():
            announcement = Announcement(
                title='Test Announcement',
                message='Test message',
                priority='high',
                created_by=admin_user.id
            )
            
            assert announcement.title == 'Test Announcement'
            assert announcement.message == 'Test message'
            assert announcement.priority == 'high'
            assert announcement.is_active is True
    
    def test_announcement_to_dict(self, app, announcement):
        """Test announcement serialization."""
        with app.app_context():
            ann_dict = announcement.to_dict()
            
            assert ann_dict['title'] == announcement.title
            assert ann_dict['message'] == announcement.message
            assert ann_dict['priority'] == announcement.priority
            assert 'created_at' in ann_dict
    
    def test_announcement_with_expiry(self, app, admin_user):
        """Test announcement with expiration date."""
        with app.app_context():
            from models import db
            expiry = datetime.now(timezone.utc) + timedelta(days=7)
            
            announcement = Announcement(
                title='Limited Time',
                message='This will expire',
                priority='normal',
                created_by=admin_user.id,
                expires_at=expiry
            )
            db.session.add(announcement)
            db.session.commit()
            
            assert announcement.expires_at is not None
            assert announcement.expires_at > datetime.now(timezone.utc)


# ==================== Model Integration Tests ====================

class TestModelIntegration:
    """Test interactions between multiple models."""
    
    def test_complete_order_workflow(self, app, user, menu_items):
        """Test complete order creation workflow."""
        with app.app_context():
            from models import db
            
            # Create order
            order = Order(user_id=user.id, status='pending')
            db.session.add(order)
            db.session.flush()
            
            # Add items
            for item in menu_items[:3]:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item.id,
                    quantity=2,
                    unit_price=item.price
                )
                db.session.add(order_item)
            
            db.session.commit()
            
            # Verify
            assert len(list(order.items)) == 3
            total = order.calculate_total()
            assert total > 0
    
    def test_cascade_delete_order(self, app, order):
        """Test that deleting an order cascades to order items."""
        with app.app_context():
            from models import db
            
            order_id = order.id
            item_count = OrderItem.query.filter_by(order_id=order_id).count()
            
            assert item_count > 0
            
            db.session.delete(order)
            db.session.commit()
            
            # Check items are deleted
            item_count_after = OrderItem.query.filter_by(order_id=order_id).count()
            assert item_count_after == 0
    
    def test_user_order_history(self, app, user, menu_items):
        """Test retrieving user's order history."""
        with app.app_context():
            from models import db
            
            # Create multiple orders
            for i in range(3):
                order = Order(user_id=user.id, status='completed')
                db.session.add(order)
            
            db.session.commit()
            
            # Query orders
            orders = Order.query.filter_by(user_id=user.id).all()
            assert len(orders) >= 3