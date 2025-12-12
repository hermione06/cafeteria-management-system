"""
Tests for Menu API endpoints
"""
import pytest
import json


class TestGetMenu:
    """Test GET /api/menu endpoint"""
    
    def test_get_empty_menu(self, client):
        """Test getting menu when no items exist"""
        response = client.get('/api/menu')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'items' in data
        assert len(data['items']) == 0
    
    def test_get_menu_with_items(self, client, multiple_menu_items):
        """Test getting menu with multiple items"""
        response = client.get('/api/menu')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 5
        assert 'pagination' in data
    
    def test_filter_by_category(self, client, multiple_menu_items):
        """Test filtering menu by category"""
        response = client.get('/api/menu?category=beverages')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 2
        for item in data['items']:
            assert item['category'] == 'beverages'
    
    def test_filter_available_only(self, client, multiple_menu_items):
        """Test filtering only available items"""
        response = client.get('/api/menu?available=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 4  # One item is unavailable
        for item in data['items']:
            assert item['is_available'] is True
    
    def test_show_all_items(self, client, multiple_menu_items):
        """Test showing all items including unavailable"""
        response = client.get('/api/menu?available=false')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 5
    
    def test_search_menu(self, client, multiple_menu_items):
        """Test searching menu items by name"""
        response = client.get('/api/menu?search=coffee')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 2  # Espresso and Cappuccino
    
    def test_pagination(self, client, multiple_menu_items):
        """Test menu pagination"""
        response = client.get('/api/menu?per_page=2&page=1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 2
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 2
        assert data['pagination']['total_items'] == 5


class TestGetMenuItem:
    """Test GET /api/menu/<id> endpoint"""
    
    def test_get_existing_item(self, client, menu_item):
        """Test getting a specific menu item"""
        response = client.get(f'/api/menu/{menu_item.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == menu_item.id
        assert data['name'] == menu_item.name
        assert data['price'] == menu_item.price
    
    def test_get_nonexistent_item(self, client):
        """Test getting non-existent menu item"""
        response = client.get('/api/menu/9999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestGetCategories:
    """Test GET /api/menu/categories endpoint"""
    
    def test_get_categories(self, client, multiple_menu_items):
        """Test getting all categories"""
        response = client.get('/api/menu/categories')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'categories' in data
        assert len(data['categories']) == 4
        assert 'beverages' in data['categories']
        assert 'food' in data['categories']


class TestCreateMenuItem:
    """Test POST /api/menu endpoint"""
    
    def test_create_item_as_admin(self, client, admin_headers):
        """Test creating menu item as admin"""
        item_data = {
            'name': 'New Coffee',
            'description': 'Fresh coffee',
            'price': 4.00,
            'category': 'beverages',
            'is_available': True,
            'stock_quantity': 50
        }
        response = client.post(
            '/api/menu',
            data=json.dumps(item_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Menu item created successfully'
        assert data['item']['name'] == 'New Coffee'
        assert data['item']['price'] == 4.00
    
    def test_create_item_without_auth(self, client):
        """Test creating menu item without authentication"""
        item_data = {
            'name': 'New Coffee',
            'price': 4.00,
            'category': 'beverages'
        }
        response = client.post(
            '/api/menu',
            data=json.dumps(item_data),
            content_type='application/json'
        )
        assert response.status_code == 401
    
    def test_create_item_as_regular_user(self, client, auth_headers):
        """Test creating menu item as regular user (should fail)"""
        item_data = {
            'name': 'New Coffee',
            'price': 4.00,
            'category': 'beverages'
        }
        response = client.post(
            '/api/menu',
            data=json.dumps(item_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_create_item_missing_required_fields(self, client, admin_headers):
        """Test creating menu item with missing required fields"""
        item_data = {
            'name': 'New Coffee'
            # Missing price and category
        }
        response = client.post(
            '/api/menu',
            data=json.dumps(item_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_item_invalid_price(self, client, admin_headers):
        """Test creating menu item with negative price"""
        item_data = {
            'name': 'New Coffee',
            'price': -5.00,
            'category': 'beverages'
        }
        response = client.post(
            '/api/menu',
            data=json.dumps(item_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_item_invalid_category(self, client, admin_headers):
        """Test creating menu item with invalid category"""
        item_data = {
            'name': 'New Coffee',
            'price': 4.00,
            'category': 'invalid_category'
        }
        response = client.post(
            '/api/menu',
            data=json.dumps(item_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid category' in data['error']


class TestUpdateMenuItem:
    """Test PUT /api/menu/<id> endpoint"""
    
    def test_update_item_as_admin(self, client, admin_headers, menu_item):
        """Test updating menu item as admin"""
        update_data = {
            'name': 'Updated Coffee',
            'price': 5.00
        }
        response = client.put(
            f'/api/menu/{menu_item.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['item']['name'] == 'Updated Coffee'
        assert data['item']['price'] == 5.00
    
    def test_update_item_as_staff(self, client, staff_headers, menu_item):
        """Test updating menu item as staff"""
        update_data = {'price': 4.50}
        response = client.put(
            f'/api/menu/{menu_item.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=staff_headers
        )
        assert response.status_code == 200
    
    def test_update_item_as_user(self, client, auth_headers, menu_item):
        """Test updating menu item as regular user (should fail)"""
        update_data = {'price': 4.50}
        response = client.put(
            f'/api/menu/{menu_item.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_update_nonexistent_item(self, client, admin_headers):
        """Test updating non-existent item"""
        update_data = {'price': 4.50}
        response = client.put(
            '/api/menu/9999',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 404
    
    def test_update_item_invalid_price(self, client, admin_headers, menu_item):
        """Test updating with invalid price"""
        update_data = {'price': -5.00}
        response = client.put(
            f'/api/menu/{menu_item.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400


class TestDeleteMenuItem:
    """Test DELETE /api/menu/<id> endpoint"""
    
    def test_delete_item_as_admin(self, client, admin_headers, menu_item):
        """Test deleting menu item as admin"""
        response = client.delete(
            f'/api/menu/{menu_item.id}',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message']
        
        # Verify item is deleted
        get_response = client.get(f'/api/menu/{menu_item.id}')
        assert get_response.status_code == 404
    
    def test_delete_item_as_staff(self, client, staff_headers, menu_item):
        """Test deleting menu item as staff (should fail)"""
        response = client.delete(
            f'/api/menu/{menu_item.id}',
            headers=staff_headers
        )
        assert response.status_code == 403
    
    def test_delete_item_as_user(self, client, auth_headers, menu_item):
        """Test deleting menu item as regular user (should fail)"""
        response = client.delete(
            f'/api/menu/{menu_item.id}',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_delete_nonexistent_item(self, client, admin_headers):
        """Test deleting non-existent item"""
        response = client.delete(
            '/api/menu/9999',
            headers=admin_headers
        )
        assert response.status_code == 404


class TestToggleAvailability:
    """Test PATCH /api/menu/<id>/availability endpoint"""
    
    def test_toggle_availability_as_admin(self, client, admin_headers, menu_item):
        """Test toggling availability as admin"""
        toggle_data = {'is_available': False}
        response = client.patch(
            f'/api/menu/{menu_item.id}/availability',
            data=json.dumps(toggle_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['item']['is_available'] is False
    
    def test_toggle_availability_as_staff(self, client, staff_headers, menu_item):
        """Test toggling availability as staff"""
        toggle_data = {'is_available': False}
        response = client.patch(
            f'/api/menu/{menu_item.id}/availability',
            data=json.dumps(toggle_data),
            content_type='application/json',
            headers=staff_headers
        )
        assert response.status_code == 200
    
    def test_toggle_availability_missing_field(self, client, admin_headers, menu_item):
        """Test toggling without is_available field"""
        response = client.patch(
            f'/api/menu/{menu_item.id}/availability',
            data=json.dumps({}),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400