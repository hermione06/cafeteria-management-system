import sys
import os

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import app

def test_index_route():
    """Test the homepage route"""
    client = app.test_client()
    response = client.get('/')
    
    assert response.status_code == 200
    assert b'Welcome to Cafeteria Management System' in response.data

def test_health_check():
    """Test the health check endpoint"""
    client = app.test_client()
    response = client.get('/health')
    
    assert response.status_code == 200
    assert b'healthy' in response.data

def test_get_menu():
    """Test getting all menu items"""
    client = app.test_client()
    response = client.get('/menu')
    
    assert response.status_code == 200
    assert b'menu' in response.data

def test_get_menu_item_success():
    """Test getting a specific menu item that exists"""
    client = app.test_client()
    response = client.get('/menu/1')
    
    assert response.status_code == 200
    assert b'Coffee' in response.data

def test_get_menu_item_not_found():
    """Test getting a menu item that doesn't exist"""
    client = app.test_client()
    response = client.get('/menu/999')
    
    assert response.status_code == 404
    assert b'Item not found' in response.data