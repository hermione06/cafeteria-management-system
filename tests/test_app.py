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
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

# ===== Menu Endpoints Tests =====

def test_index_route(client):
    """Test the homepage route"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Cafeteria Management System' in response.data

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert b'healthy' in response.data

def test_get_menu(client):
    """Test getting all menu items"""
    response = client.get('/menu')
    assert response.status_code == 200
    assert b'menu' in response.data

def test_get_menu_item_success(client):
    """Test getting a specific menu item that exists"""
    response = client.get('/menu/1')
    assert response.status_code == 200
    assert b'Coffee' in response.data

def test_get_menu_item_not_found(client):
    """Test getting a menu item that doesn't exist"""
    response = client.get('/menu/999')
    assert response.status_code == 404
    assert b'Item not found' in response.data

def test_get_menu_by_category(client):
    """Test filtering menu items by category"""
    response = client.get('/menu/category/Beverages')
    assert response.status_code == 200
    assert b'Coffee' in response.data
    assert b'Beverages' in response.data

def test_get_menu_by_empty_category(client):
    """Test filtering menu items by non-existent category"""
    response = client.get('/menu/category/Desserts')
    assert response.status_code == 200
    assert b'No items found' in response.data

# ===== User Model Tests =====

def test_user_model_creation(client):
    """Test creating a user model instance"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com', role='customer')
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'customer'
        assert user.is_active is True

def test_user_to_dict(client):
    """Test user to_dict method"""
    with app.app_context():
        user = User(username='dictuser', email='dict@example.com')
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        assert user_dict['username'] == 'dictuser'
        assert user_dict['email'] == 'dict@example.com'
        assert 'created_at' in user_dict
        assert 'updated_at' in user_dict

def test_user_validate_role():
    """Test role validation method"""
    assert User.validate_role('customer') is True
    assert User.validate_role('staff') is True
    assert User.validate_role('admin') is True
    assert User.validate_role('invalid') is False

# ===== User API Endpoints Tests =====

def test_get_users_empty(client):
    """Test getting users when database is empty"""
    response = client.get('/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['users'] == []

def test_create_user_success(client):
    """Test creating a new user successfully"""
    user_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'role': 'customer'
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
        'email': 'first@example.com'
    }
    client.post('/users',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Try to create another user with same username
    user_data2 = {
        'username': 'duplicate',
        'email': 'second@example.com'
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
        'email': 'duplicate@example.com'
    }
    client.post('/users',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Try to create another user with same email
    user_data2 = {
        'username': 'user2',
        'email': 'duplicate@example.com'
    }
    response = client.post('/users',
                          data=json.dumps(user_data2),
                          content_type='application/json')
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'Email already exists' in data['error']

def test_get_user_by_id(client):
    """Test getting a specific user by ID"""
    # Create a user first
    user_data = {
        'username': 'getuser',
        'email': 'get@example.com'
    }
    create_response = client.post('/users',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
    user_id = json.loads(create_response.data)['user']['id']
    
    # Get the user
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == 'getuser'

def test_get_user_not_found(client):
    """Test getting a non-existent user"""
    response = client.get('/users/9999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'User not found' in data['error']

def test_update_user_success(client):
    """Test updating a user successfully"""
    # Create a user first
    user_data = {
        'username': 'updateuser',
        'email': 'update@example.com'
    }
    create_response = client.post('/users',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
    user_id = json.loads(create_response.data)['user']['id']
    
    # Update the user
    update_data = {
        'username': 'updateduser',
        'role': 'staff'
    }
    response = client.put(f'/users/{user_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user']['username'] == 'updateduser'
    assert data['user']['role'] == 'staff'

def test_update_user_not_found(client):
    """Test updating a non-existent user"""
    update_data = {'username': 'newname'}
    response = client.put('/users/9999',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 404

def test_delete_user_success(client):
    """Test deleting a user successfully"""
    # Create a user first
    user_data = {
        'username': 'deleteuser',
        'email': 'delete@example.com'
    }
    create_response = client.post('/users',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
    user_id = json.loads(create_response.data)['user']['id']
    
    # Delete the user
    response = client.delete(f'/users/{user_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'deleted successfully' in data['message']
    
    # Verify user is deleted
    get_response = client.get(f'/users/{user_id}')
    assert get_response.status_code == 404

def test_delete_user_not_found(client):
    """Test deleting a non-existent user"""
    response = client.delete('/users/9999')
    assert response.status_code == 404