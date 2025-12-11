# cafeteria-management-system/tests/conftest.py

import pytest
from datetime import timedelta, datetime, timezone
from app import create_app, db
from models import User, UserRole, MenuItem, Order, OrderItem, Announcement
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for testing."""
    # Use the 'testing' configuration for in-memory SQLite DB
    app = create_app('testing')
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def init_db(app):
    """Fixture to ensure a clean database for each test."""
    with app.app_context():
        # Clean slate for each test function
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield db

@pytest.fixture
def users_data():
    """Returns static data for test users."""
    return {
        'student': {'username': 'student_user', 'email': 'student@test.com', 'password': 'Password123!', 'role': UserRole.STUDENT},
        'staff': {'username': 'staff_user', 'email': 'staff@test.com', 'password': 'Password123!', 'role': UserRole.STAFF},
        'admin': {'username': 'admin_user', 'email': 'admin@test.com', 'password': 'Password123!', 'role': UserRole.ADMIN}
    }

@pytest.fixture
def setup_users(init_db, users_data):
    """Creates and commits test users to the database."""
    users = {}
    with init_db.app.app_context():
        for role, data in users_data.items():
            user = User(username=data['username'], email=data['email'], role=data['role'], is_verified=True)
            user.set_password(data['password'])
            init_db.session.add(user)
            users[role] = user

        # Add an unverified user for specific auth tests
        unverified_user = User(username='unverified', email='unverified@t.com', role=UserRole.STUDENT)
        unverified_user.set_password('Password123!')
        init_db.session.add(unverified_user)
        users['unverified'] = unverified_user

        init_db.session.commit()
        return users

@pytest.fixture
def get_auth_tokens(app, setup_users):
    """Returns JWT access tokens for test users."""
    tokens = {}
    with app.app_context():
        for role, user in setup_users.items():
            # Use long expiry for testing purposes
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
            tokens[role] = access_token
        return tokens

@pytest.fixture
def auth_headers(get_auth_tokens):
    """Returns authorization headers for test users."""
    headers = {}
    for role, token in get_auth_tokens.items():
        headers[role] = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    return headers

@pytest.fixture
def setup_menu(init_db):
    """Creates and commits test menu items."""
    with init_db.app.app_context():
        menu_items = [
            MenuItem(name="Burger", description="Beef patty", price=5.00, category="Main", is_available=True, stock=10),
            MenuItem(name="Fries", description="Golden crispy fries", price=2.50, category="Side", is_available=True, stock=50),
            MenuItem(name="Soda", description="Cola drink", price=1.50, category="Drink", is_available=False, stock=0),
            MenuItem(name="Salad", description="Healthy garden salad", price=4.00, category="Main", is_available=True, stock=20)
        ]
        init_db.session.add_all(menu_items)
        init_db.session.commit()
        return {item.name: item for item in menu_items}

@pytest.fixture
def setup_orders(init_db, setup_users, setup_menu):
    """Creates a couple of test orders."""
    from src.order import OrderHandler 

    user_id = setup_users['student'].id
    item_id_1 = setup_menu['Burger'].id
    item_id_2 = setup_menu['Fries'].id

    with init_db.app.app_context():
        # Order 1 (New, Unpaid)
        order1 = OrderHandler.create_order(user_id)
        OrderHandler.add_item(order1.id, item_id_1, 2)
        OrderHandler.add_item(order1.id, item_id_2, 1)

        # Order 2 (Completed and Paid)
        order2 = OrderHandler.create_order(user_id)
        OrderHandler.update_status(order2.id, 'completed')
        OrderHandler.mark_paid(order2.id)

        init_db.session.commit()
        return [order1, order2]