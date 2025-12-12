"""
Test configuration and fixtures
"""
import pytest
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token

from src.app import create_app
from src.models import db, User, MenuItem, Order, OrderItem, Announcement


@pytest.fixture(scope='function')
def app():
    """Create and configure a test app instance"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a database session for tests"""
    with app.app_context():
        yield db.session


# ==================== USER FIXTURES ====================

@pytest.fixture
def admin_user(app):
    """Create an admin user"""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@test.com',
            role='admin',
            is_active=True,
            is_verified=True
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def staff_user(app):
    """Create a staff user"""
    with app.app_context():
        user = User(
            username='staff',
            email='staff@test.com',
            role='staff',
            is_active=True,
            is_verified=True
        )
        user.set_password('staff123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def regular_user(app):
    """Create a regular user"""
    with app.app_context():
        user = User(
            username='user',
            email='user@test.com',
            role='user',
            is_active=True,
            is_verified=True
        )
        user.set_password('user123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def inactive_user(app):
    """Create an inactive user"""
    with app.app_context():
        user = User(
            username='inactive',
            email='inactive@test.com',
            role='user',
            is_active=False,
            is_verified=True
        )
        user.set_password('inactive123')
        db.session.add(user)
        db.session.commit()
        return user


# ==================== TOKEN FIXTURES ====================

@pytest.fixture
def admin_token(app, admin_user):
    """Create admin JWT token"""
    with app.app_context():
        return create_access_token(
            identity=admin_user.id,
            additional_claims={
                'role': admin_user.role,
                'username': admin_user.username
            }
        )


@pytest.fixture
def staff_token(app, staff_user):
    """Create staff JWT token"""
    with app.app_context():
        return create_access_token(
            identity=staff_user.id,
            additional_claims={
                'role': staff_user.role,
                'username': staff_user.username
            }
        )


@pytest.fixture
def user_token(app, regular_user):
    """Create regular user JWT token"""
    with app.app_context():
        return create_access_token(
            identity=regular_user.id,
            additional_claims={
                'role': regular_user.role,
                'username': regular_user.username
            }
        )


@pytest.fixture
def auth_headers(user_token):
    """Create authorization headers with user token"""
    return {'Authorization': f'Bearer {user_token}'}


@pytest.fixture
def admin_headers(admin_token):
    """Create authorization headers with admin token"""
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture
def staff_headers(staff_token):
    """Create authorization headers with staff token"""
    return {'Authorization': f'Bearer {staff_token}'}


# ==================== MENU ITEM FIXTURES ====================

@pytest.fixture
def menu_item(app):
    """Create a single menu item"""
    with app.app_context():
        item = MenuItem(
            name='Test Coffee',
            description='A test coffee item',
            price=3.50,
            category='beverages',
            is_available=True,
            stock_quantity=100
        )
        db.session.add(item)
        db.session.commit()
        return item


@pytest.fixture
def unavailable_menu_item(app):
    """Create an unavailable menu item"""
    with app.app_context():
        item = MenuItem(
            name='Unavailable Item',
            description='This item is not available',
            price=5.00,
            category='food',
            is_available=False,
            stock_quantity=0
        )
        db.session.add(item)
        db.session.commit()
        return item


@pytest.fixture
def multiple_menu_items(app):
    """Create multiple menu items across categories"""
    with app.app_context():
        items = [
            MenuItem(
                name='Espresso',
                description='Strong coffee',
                price=2.50,
                category='beverages',
                is_available=True,
                stock_quantity=50
            ),
            MenuItem(
                name='Cappuccino',
                description='Coffee with milk',
                price=3.50,
                category='beverages',
                is_available=True,
                stock_quantity=50
            ),
            MenuItem(
                name='Sandwich',
                description='Ham sandwich',
                price=5.00,
                category='food',
                is_available=True,
                stock_quantity=20
            ),
            MenuItem(
                name='Cookie',
                description='Chocolate cookie',
                price=2.00,
                category='snacks',
                is_available=True,
                stock_quantity=100
            ),
            MenuItem(
                name='Cake',
                description='Chocolate cake',
                price=4.50,
                category='desserts',
                is_available=False,
                stock_quantity=0
            ),
        ]
        db.session.add_all(items)
        db.session.commit()
        return items


# ==================== ORDER FIXTURES ====================

@pytest.fixture
def order(app, regular_user, menu_item):
    """Create a test order with one item"""
    with app.app_context():
        order = Order(
            user_id=regular_user.id,
            status='pending',
            is_paid=False
        )
        db.session.add(order)
        db.session.flush()
        
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=2,
            unit_price=menu_item.price
        )
        db.session.add(order_item)
        db.session.commit()
        return order


@pytest.fixture
def completed_order(app, regular_user, menu_item):
    """Create a completed order"""
    with app.app_context():
        order = Order(
            user_id=regular_user.id,
            status='completed',
            is_paid=True,
            payment_method='card',
            completed_at=datetime.now(timezone.utc)
        )
        db.session.add(order)
        db.session.flush()
        
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=1,
            unit_price=menu_item.price
        )
        db.session.add(order_item)
        db.session.commit()
        return order


@pytest.fixture
def multiple_orders(app, regular_user, multiple_menu_items):
    """Create multiple orders"""
    with app.app_context():
        orders = []
        
        # Pending order
        order1 = Order(
            user_id=regular_user.id,
            status='pending',
            is_paid=False
        )
        db.session.add(order1)
        db.session.flush()
        
        order_item1 = OrderItem(
            order_id=order1.id,
            menu_item_id=multiple_menu_items[0].id,
            quantity=2,
            unit_price=multiple_menu_items[0].price
        )
        db.session.add(order_item1)
        orders.append(order1)
        
        # Completed order
        order2 = Order(
            user_id=regular_user.id,
            status='completed',
            is_paid=True,
            completed_at=datetime.now(timezone.utc)
        )
        db.session.add(order2)
        db.session.flush()
        
        order_item2 = OrderItem(
            order_id=order2.id,
            menu_item_id=multiple_menu_items[2].id,
            quantity=1,
            unit_price=multiple_menu_items[2].price
        )
        db.session.add(order_item2)
        orders.append(order2)
        
        db.session.commit()
        return orders


# ==================== ANNOUNCEMENT FIXTURES ====================

@pytest.fixture
def announcement(app, admin_user):
    """Create a test announcement"""
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
        return announcement


@pytest.fixture
def expired_announcement(app, admin_user):
    """Create an expired announcement"""
    with app.app_context():
        announcement = Announcement(
            title='Expired Announcement',
            message='This announcement has expired',
            priority='low',
            is_active=True,
            created_by=admin_user.id,
            expires_at=datetime.now(timezone.utc)
        )
        db.session.add(announcement)
        db.session.commit()
        return announcement


@pytest.fixture
def multiple_announcements(app, admin_user):
    """Create multiple announcements"""
    with app.app_context():
        announcements = [
            Announcement(
                title='High Priority',
                message='Important message',
                priority='high',
                is_active=True,
                created_by=admin_user.id
            ),
            Announcement(
                title='Normal Priority',
                message='Regular message',
                priority='normal',
                is_active=True,
                created_by=admin_user.id
            ),
            Announcement(
                title='Low Priority',
                message='Less important',
                priority='low',
                is_active=True,
                created_by=admin_user.id
            ),
            Announcement(
                title='Inactive',
                message='Not shown',
                priority='normal',
                is_active=False,
                created_by=admin_user.id
            ),
        ]
        db.session.add_all(announcements)
        db.session.commit()
        return announcements