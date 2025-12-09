import sys
import os
import json

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest

# Set testing config BEFORE importing app
os.environ['FLASK_ENV'] = 'testing'

from app import app, db
from models import User

@pytest.fixture
def client():
    """Create a test client with in-memory database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"check_same_thread": False}
    }
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def sample_menu_items(client):
    """Create sample menu items in the database for testing"""
    try:
        from models import MenuItem
    except ImportError:
        pytest.skip("MenuItem model not found")
    
    with app.app_context():
        # Clear existing menu items
        MenuItem.query.delete()
        
        # Add test menu items
        items = [
            MenuItem(name="Coffee", price=2.50, category="Beverages", description="Hot coffee"),
            MenuItem(name="Sandwich", price=5.00, category="Food", description="Fresh sandwich"),
            MenuItem(name="Salad", price=4.50, category="Food", description="Green salad")
        ]
        
        for item in items:
            db.session.add(item)
        
        db.session.commit()
        
        # Return the created items for use in tests
        yield MenuItem.query.all()
        
        # Cleanup
        MenuItem.query.delete()
        db.session.commit()

# ===== Menu Endpoints Tests =====

def test_index_route(client):
    """Test the homepage route"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to UFAZ Cafeteria' in response.data

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert b'healthy' in response.data

# ===== OLD MENU TESTS (Commented out - for in-memory menu system) =====
# def test_get_menu(client):
#     """Test getting all menu items"""
#     response = client.get('/menu')
#     assert response.status_code == 200
#     assert b'menu' in response.data

# def test_get_menu_item_success(client):
#     """Test getting a specific menu item that exists"""
#     response = client.get('/menu/1')
#     assert response.status_code == 200
#     assert b'Coffee' in response.data

# def test_get_menu_item_not_found(client):
#     """Test getting a menu item that doesn't exist"""
#     response = client.get('/menu/999')
#     assert response.status_code == 404
#     assert b'Item not found' in response.data

# def test_get_menu_by_category(client):
#     """Test filtering menu items by category"""
#     response = client.get('/menu/category/Beverages')
#     assert response.status_code == 200
#     assert b'Coffee' in response.data
#     assert b'Beverages' in response.data

# def test_get_menu_by_empty_category(client):
#     """Test filtering menu items by non-existent category"""
#     response = client.get('/menu/category/Desserts')
#     assert response.status_code == 200
#     assert b'No items found' in response.data

# ===== NEW MENU TESTS (Database-backed menu system) =====

def test_get_menu_new(client, sample_menu_items):
    """Test getting all menu items from database"""
    response = client.get('/menu/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 3
    # Check if Coffee is in the menu
    menu_names = [item['name'] for item in data]
    assert 'Coffee' in menu_names

def test_get_menu_empty_database(client):
    """Test getting menu when database is empty"""
    response = client.get('/menu/')
    # The route returns 404 when no menu items exist, not 200 with empty array
    assert response.status_code == 404

def test_get_menu_item_success_new(client, sample_menu_items):
    """Test getting a specific menu item that exists"""
    # Get the first item's ID
    item_id = sample_menu_items[0].id
    response = client.get(f'/menu/{item_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Coffee'
    assert data['price'] == 2.50

def test_get_menu_item_not_found_new(client, sample_menu_items):
    """Test getting a menu item that doesn't exist"""
    response = client.get('/menu/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data or 'message' in data

def test_get_menu_by_category_new(client, sample_menu_items):
    """Test filtering menu items by category"""
    response = client.get('/menu/category/Beverages')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]['name'] == 'Coffee'
    assert data[0]['category'] == 'Beverages'

def test_get_menu_by_empty_category_new(client, sample_menu_items):
    """Test filtering menu items by non-existent category"""
    response = client.get('/menu/category/Desserts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

# ===== User Model Tests =====

def test_user_model_creation(client):
    """Test creating a user model instance"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com', role='customer')
        user.set_password("testpassword")  # ✅ Hash and set password
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password("testpassword") is True
        assert user.role == 'customer'
        assert user.is_active is True

def test_user_to_dict(client):
    """Test user to_dict method"""
    with app.app_context():
        user = User(username='dictuser', email='dict@example.com')
        user.set_password("dictpassword123")
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        assert user_dict['username'] == 'dictuser'
        assert user_dict['email'] == 'dict@example.com'
        assert 'created_at' in user_dict
        assert 'updated_at' in user_dict

def test_user_validate_role():
    """Test role validation method"""
    assert User.validate_role('customer') is False
    assert User.validate_role('user') is True
    assert User.validate_role('admin') is True
    assert User.validate_role('invalid') is False

# ===== User API Endpoints Tests =====

# def test_get_users_authenticated_admin(client):
#     """Test getting users when admin is logged in"""
#     admin = User(username='admin', email='admin@example.com', role='admin')
#     admin.set_password('password123')
#     admin.verify_email()
#     db.session.add(admin)
#     db.session.commit()

#     # Log in as admin
#     login_response = client.post('/auth/login', json={
#         'username': 'admin',
#         'password': 'password123'
#     })
#     assert login_response.status_code == 200
#     token = login_response.get_json()['access_token']

#     # Get users
#     response = client.get('/users', headers={'Authorization': f'Bearer {token}'})
#     assert response.status_code == 200

#     data = response.get_json()
#     assert len(data['users']) == 1
#     assert data['users'][0]['username'] == 'admin'


def test_create_user_success(client):
    """Test creating a new user successfully"""
    user_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'role': 'user'
    }
    
    response = client.post('/users', 
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User created successfully'
    assert data['user']['username'] == 'newuser'
    assert data['user']['email'] == 'newuser@example.com'

def test_create_user_missing_fields(client):
    """Test creating user without required fields"""
    user_data = {'username': 'incomplete'}
    response = client.post('/users',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_create_user_invalid_role(client):
    """Test creating user with invalid role"""
    user_data = {
        'username': 'baduser',
        'email': 'bad@example.com',
        'role': 'superuser'
    }
    response = client.post('/users',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid role' in data['error']

def test_create_user_duplicate_username(client):
    """Test creating user with duplicate username"""
    user_data = {
        'username': 'duplicate',
        'email': 'first@example.com',
        'password': 'password123'
    }
    client.post('/users',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Try to create another user with same username
    user_data2 = {
        'username': 'duplicate',
        'email': 'second@example.com',
        'password': 'password456'
    }
    response = client.post('/users',
                          data=json.dumps(user_data2),
                          content_type='application/json')
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'Username already exists' in data['error']

def test_create_user_duplicate_email(client):
    """Test creating user with duplicate email"""
    user_data = {
        'username': 'user1',
        'email': 'duplicate@example.com',
        'password': 'password123'
    }
    client.post('/users',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Try to create another user with same email
    user_data2 = {
        'username': 'user2',
        'email': 'duplicate@example.com',
        'password': 'password456'
    }
    response = client.post('/users',
                          data=json.dumps(user_data2),
                          content_type='application/json')
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'Email already exists' in data['error']

# def test_get_user_by_id(client):
#     """Test getting a specific user by ID"""
#     # Create a user first
#     user_data = {
#         'username': 'getuser',
#         'email': 'get@example.com',
#         'password': 'password123'
#     }
#     create_response = client.post('/users',
#                         data=json.dumps(user_data),
#                         content_type='application/json')
#     user = json.loads(create_response.data)['user']
#     user_id = user['id']
    
#     # Verify the user's email before logging in
#     with app.app_context():
#         test_user = db.session.get(User, user_id)
#         test_user.verify_email()
#         db.session.commit()
    
#     # Log in to get JWT token
#     login_response = client.post('/auth/login', json={
#         'username': 'getuser',
#         'password': 'password123'
#     })
#     token = login_response.get_json()['access_token']
    
#     # Now include token in Authorization header
#     response = client.get(f'/users/{user_id}',
#                           headers={'Authorization': f'Bearer {token}'})
    
#     assert response.status_code == 200
#     data = json.loads(response.data)
#     assert data['username'] == 'getuser'

# def test_get_user_not_found(client):
#     """Test getting a non-existent user"""
#     # Create an admin user to test accessing non-existent users
#     user_data = {
#         'username': 'adminuser',
#         'email': 'admin@example.com',
#         'password': 'password123',
#         'role': 'admin'
#     }
#     create_response = client.post('/users', data=json.dumps(user_data), content_type='application/json')
    
#     # Verify the admin user's email before logging in
#     user_id = json.loads(create_response.data)['user']['id']
#     with app.app_context():
#         test_user = db.session.get(User, user_id)
#         test_user.verify_email()
#         db.session.commit()

#     login_response = client.post('/auth/login', json={
#         'username': 'adminuser',
#         'password': 'password123'
#     })
#     token = login_response.get_json()['access_token']

#     # Now test a missing user with admin token
#     response = client.get('/users/9999', headers={'Authorization': f'Bearer {token}'})
#     assert response.status_code == 404
#     data = json.loads(response.data)
#     assert 'User not found' in data['error']

def test_update_user_success(client):
    """Test updating a user successfully"""
    # Create a user first
    user_data = {
        'username': 'updateuser',
        'email': 'update@example.com',
        'password': 'password123'
    }
    create_response = client.post('/users',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
    user_id = json.loads(create_response.data)['user']['id']
    
    # Update the user
    update_data = {
        'username': 'updateduser',
        'role': 'admin'
    }
    response = client.put(f'/users/{user_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user']['username'] == 'updateduser'
    assert data['user']['role'] == 'admin'

def test_update_user_not_found(client):
    """Test updating a non-existent user"""
    update_data = {'username': 'newname'}
    response = client.put('/users/9999',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 404

# def test_delete_user_success(client):
#     """Test deleting a user successfully"""
#     # Create a user first
#     user_data = {
#         'username': 'deleteuser',
#         'email': 'delete@example.com',
#         'password': 'password123'
#     }
#     create_response = client.post('/users',
#                                   data=json.dumps(user_data),
#                                   content_type='application/json')
#     user_id = json.loads(create_response.data)['user']['id']

#     # Verify the user's email before logging in
#     with app.app_context():
#         test_user = db.session.get(User, user_id)
#         test_user.verify_email()
#         db.session.commit()

#     # Log in to get token
#     login_response = client.post('/auth/login', json={
#         'username': 'deleteuser',
#         'password': 'password123'
#     })
#     token = json.loads(login_response.data)['access_token']

#     # Delete the user (include token)
#     delete_response = client.delete(f'/users/{user_id}',
#                                     headers={'Authorization': f'Bearer {token}'})
#     assert delete_response.status_code == 200
#     data = json.loads(delete_response.data)
#     assert 'deleted successfully' in data['message']

#     # Try to get the deleted user (also include token)
#     get_response = client.get(f'/users/{user_id}',
#                               headers={'Authorization': f'Bearer {token}'})
#     assert get_response.status_code == 404

def test_delete_user_not_found(client):
    """Test deleting a non-existent user"""
    response = client.delete('/users/9999')
    assert response.status_code == 404


# TODO: 
# If you want to make testing easier and avoid repeating set_password() everywhere, you can modify your User model's __init__ like this:

# def __init__(self, username, email, password=None, **kwargs):
#     super().__init__(username=username, email=email, **kwargs)
#     if password:
#         self.set_password(password)


# Then your test can simply be:

# user = User(username='dictuser', email='dict@example.com', password='secure123')
