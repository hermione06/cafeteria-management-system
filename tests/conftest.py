"""
Pytest configuration and shared fixtures for all tests.
This file provides common test fixtures and setup.
"""
import sys
import os
from datetime import datetime, timezone

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from app import create_app
from models import db, User, MenuItem, Order, OrderItem, Announcement


@pytest.fixture(scope='function')
def app():
    """Create and configure a test application instance."""
    os.environ['FLASK_ENV'] = 'testing'
    
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'WTF_CSRF_ENABLED': False,
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def session(app):
    """Create a database session for tests."""
    with app.app_context():
        yield db.session


# ==================== User Fixtures ====================

@pytest.fixture
def user(app):
    """Create a regular verified user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            role='user'
        )
        user.set_password('TestPass123')
        user.is_verified = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def unverified_user(app):
    """Create an unverified user."""
    with app.app_context():
        user = User(
            username='unverified',
            email='unverified@example.com',
            role='user'
        )
        user.set_password('TestPass123')
        user.is_verified = False
        user.is_active = True
        verification_token = user.generate_verification_token()
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def inactive_user(app):
    """Create an inactive user."""
    with app.app_context():
        user = User(
            username='inactive',
            email='inactive@example.com',
            role='user'
        )
        user.set_password('TestPass123')
        user.is_verified = True
        user.is_active = False
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def staff_user(app):
    """Create a staff user."""
    with app.app_context():
        user = User(
            username='staffuser',
            email='staff@example.com',
            role='staff'
        )
        user.set_password('StaffPass123')
        user.is_verified = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def admin_user(app):
    """Create an admin user."""
    with app.app_context():
        user = User(
            username='adminuser',
            email='admin@example.com',
            role='admin'
        )
        user.set_password('AdminPass123')
        user.is_verified = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


# ==================== Authentication Fixtures ====================

@pytest.fixture
def user_token(client, user):
    """Get JWT token for regular user."""
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'TestPass123'
    })
    return response.get_json()['access_token']


@pytest.fixture
def staff_token(client, staff_user):
    """Get JWT token for staff user."""
    response = client.post('/api/auth/login', json={
        'username': 'staffuser',
        'password': 'StaffPass123'
    })
    return response.get_json()['access_token']


@pytest.fixture
def admin_token(client, admin_user):
    """Get JWT token for admin user."""
    response = client.post('/api/auth/login', json={
        'username': 'adminuser',
        'password': 'AdminPass123'
    })
    return response.get_json()['access_token']


@pytest.fixture
def auth_headers(user_token):
    """Get authorization headers with user token."""
    return {'Authorization': f'Bearer {user_token}'}


@pytest.fixture
def staff_headers(staff_token):
    """Get authorization headers with staff token."""
    return {'Authorization': f'Bearer {staff_token}'}


@pytest.fixture
def admin_headers(admin_token):
    """Get authorization headers with admin token."""
    return {'Authorization': f'Bearer {admin_token}'}


# ==================== Menu Fixtures ====================

@pytest.fixture
def menu_items(app):
    """Create sample menu items."""
    with app.app_context():
        items = [
            MenuItem(
                name='Coffee',
                description='Fresh brewed coffee',
                price=2.50,
                category='beverages',
                is_available=True,
                stock_quantity=100
            ),
            MenuItem(
                name='Cappuccino',
                description='Espresso with steamed milk',
                price=3.50,
                category='beverages',
                is_available=True,
                stock_quantity=50
            ),
            MenuItem(
                name='Burger',
                description='Classic beef burger',
                price=8.99,
                category='food',
                is_available=True,
                stock_quantity=30
            ),
            MenuItem(
                name='Pizza Slice',
                description='Cheese pizza',
                price=4.50,
                category='food',
                is_available=True,
                stock_quantity=20
            ),
            MenuItem(
                name='Unavailable Item',
                description='Out of stock',
                price=5.00,
                category='snacks',
                is_available=False,
                stock_quantity=0
            )
        ]
        
        for item in items:
            db.session.add(item)
        
        db.session.commit()
        
        for item in items:
            db.session.refresh(item)
        
        return items


@pytest.fixture
def menu_item(app):
    """Create a single menu item."""
    with app.app_context():
        item = MenuItem(
            name='Test Item',
            description='Test description',
            price=5.99,
            category='food',
            is_available=True,
            stock_quantity=50
        )
        db.session.add(item)
        db.session.commit()
        db.session.refresh(item)
        return item


# ==================== Order Fixtures ====================

@pytest.fixture
def order(app, user, menu_items):
    """Create a sample order with items."""
    with app.app_context():
        order = Order(
            user_id=user.id,
            status='pending',
            is_paid=False
        )
        db.session.add(order)
        db.session.flush()
        
        # Add order items
        order_item1 = OrderItem(
            order_id=order.id,
            menu_item_id=menu_items[0].id,
            quantity=2,
            unit_price=menu_items[0].price
        )
        order_item2 = OrderItem(
            order_id=order.id,
            menu_item_id=menu_items[2].id,
            quantity=1,
            unit_price=menu_items[2].price
        )
        
        db.session.add_all([order_item1, order_item2])
        db.session.commit()
        db.session.refresh(order)
        return order


@pytest.fixture
def completed_order(app, user, menu_items):
    """Create a completed order."""
    with app.app_context():
        order = Order(
            user_id=user.id,
            status='completed',
            is_paid=True,
            completed_at=datetime.now(timezone.utc)
        )
        db.session.add(order)
        db.session.flush()
        
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_items[0].id,
            quantity=1,
            unit_price=menu_items[0].price
        )
        
        db.session.add(order_item)
        db.session.commit()
        db.session.refresh(order)
        return order


# ==================== Announcement Fixtures ====================

@pytest.fixture
def announcement(app, admin_user):
    """Create a sample announcement."""
    with app.app_context():
        announcement = Announcement(
            title='Test Announcement',
            message='This is a test announcement',
            priority='normal',
            is_active=True,
            created_by=admin_user.id
        )
        db.session.add(announcement)
        db.session.commit()
        db.session.refresh(announcement)
        return announcement


@pytest.fixture
def expired_announcement(app, admin_user):
    """Create an expired announcement."""
    with app.app_context():
        from datetime import timedelta
        announcement = Announcement(
            title='Expired Announcement',
            message='This announcement has expired',
            priority='normal',
            is_active=True,
            created_by=admin_user.id,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.session.add(announcement)
        db.session.commit()
        db.session.refresh(announcement)
        return announcement


# ==================== Helper Functions ====================

def get_json(response):
    """Extract JSON from response."""
    return response.get_json()


def assert_success(response, status_code=200):
    """Assert response is successful."""
    assert response.status_code == status_code
    assert response.is_json


def assert_error(response, status_code, error_message=None):
    """Assert response contains error."""
    assert response.status_code == status_code
    data = get_json(response)
    assert 'error' in data
    if error_message:
        assert error_message.lower() in data['error'].lower()


# Make helper functions available to all tests
pytest.get_json = get_json
pytest.assert_success = assert_success
pytest.assert_error = assert_error