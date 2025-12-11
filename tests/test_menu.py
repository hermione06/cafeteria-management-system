"""
Comprehensive tests for menu management endpoints.
Testing CRUD operations, filtering, pagination, and authorization.
"""
import pytest


# ==================== Get Menu Tests ====================

class TestGetMenu:
    """Test retrieving menu items."""
    
    def test_get_all_menu_items(self, client, menu_items):
        """Test getting all menu items."""
        response = client.get('/api/menu')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert len(data['items']) > 0
    
    def test_get_menu_filter_by_category(self, client, menu_items):
        """Test filtering menu items by category."""
        response = client.get('/api/menu?category=beverages')
        
        assert response.status_code == 200
        data = response.get_json()
        assert all(item['category'] == 'beverages' for item in data['items'])
    
    def test_get_menu_available_only(self, client, menu_items):
        """Test getting only available items."""
        response = client.get('/api/menu?available=true')
        
        assert response.status_code == 200
        data = response.get_json()
        assert all(item['is_available'] for item in data['items'])
    
    def test_get_menu_search(self, client, menu_items):
        """Test searching menu items."""
        response = client.get('/api/menu?search=coffee')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) > 0
        assert any('coffee' in item['name'].lower() for item in data['items'])
    
    def test_get_menu_pagination(self, client, menu_items):
        """Test menu pagination."""
        response = client.get('/api/menu?page=1&per_page=2')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'pagination' in data
        assert len(data['items']) <= 2
        assert data['pagination']['per_page'] == 2
    
    def test_get_menu_empty_result(self, client):
        """Test getting menu when no items exist."""
        response = client.get('/api/menu')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['items'] == []
    
    def test_get_menu_combined_filters(self, client, menu_items):
        """Test combining multiple filters."""
        response = client.get('/api/menu?category=beverages&available=true&search=coffee')
        
        assert response.status_code == 200
        data = response.get_json()
        items = data['items']
        if items:
            assert all(item['category'] == 'beverages' for item in items)
            assert all(item['is_available'] for item in items)


# ==================== Get Single Menu Item Tests ====================

class TestGetMenuItem:
    """Test retrieving single menu item."""
    
    def test_get_menu_item_by_id(self, client, menu_item):
        """Test getting specific menu item."""
        response = client.get(f'/api/menu/{menu_item.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == menu_item.id
        assert data['name'] == menu_item.name
        assert data['price'] == menu_item.price
    
    def test_get_nonexistent_menu_item(self, client):
        """Test getting non-existent menu item."""
        response = client.get('/api/menu/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'not found' in data['error'].lower()


# ==================== Get Categories Tests ====================

class TestGetCategories:
    """Test retrieving menu categories."""
    
    def test_get_categories(self, client, menu_items):
        """Test getting all menu categories."""
        response = client.get('/api/menu/categories')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'categories' in data
        assert 'beverages' in data['categories']
        assert 'food' in data['categories']
    
    def test_get_categories_empty(self, client):
        """Test getting categories when no items exist."""
        response = client.get('/api/menu/categories')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['categories'] == []


# ==================== Create Menu Item Tests ====================

class TestCreateMenuItem:
    """Test creating menu items (admin only)."""
    
    def test_create_menu_item_success(self, client, admin_headers):
        """Test successful menu item creation."""
        response = client.post('/api/menu',
                              headers=admin_headers,
                              json={
                                  'name': 'New Item',
                                  'description': 'Delicious food',
                                  'price': 7.99,
                                  'category': 'food',
                                  'is_available': True
                              })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['item']['name'] == 'New Item'
        assert data['item']['price'] == 7.99
        assert data['item']['category'] == 'food'
    
    def test_create_menu_item_minimal_fields(self, client, admin_headers):
        """Test creating item with only required fields."""
        response = client.post('/api/menu',
                              headers=admin_headers,
                              json={
                                  'name': 'Minimal Item',
                                  'price': 5.00,
                                  'category': 'snacks'
                              })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['item']['name'] == 'Minimal Item'
        assert data['item']['is_available'] is True  # Default value
    
    def test_create_menu_item_missing_name(self, client, admin_headers):
        """Test creating item without name."""
        response = client.post('/api/menu',
                              headers=admin_headers,
                              json={
                                  'price': 5.00,
                                  'category': 'food'
                              })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_create_menu_item_missing_price(self, client, admin_headers):
        """Test creating item without price."""
        response = client.post('/api/menu',
                              headers=admin_headers,
                              json={
                                  'name': 'Test Item',
                                  'category': 'food'
                              })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_create_menu_item_missing_category(self, client, admin_headers):
        """Test creating item without category."""
        response = client.post('/api/menu',
                              headers=admin_headers,
                              json={
                                  'name': 'Test Item',
                                  'price': 5.00
                              })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_create_menu_item_invalid_price(self, client, admin_headers):
        """Test creating item with negative price."""
        response = client.post('/api/menu',
                              headers=admin_headers,
                              json={
                                  'name': 'Test Item',
                                  'price': -5.00,
                                  'category': 'food'
                              })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'negative' in data['error'].lower()
    
    def test_create_menu_item_invalid_category(self, client, admin_headers):
        """Test creating item with invalid category."""
        response = client.post('/api/menu',
                              headers=admin_headers,
                              json={
                                  'name': 'Test Item',
                                  'price': 5.00,
                                  'category': 'invalid'
                              })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'invalid category' in data['error'].lower()
    
    def test_create_menu_item_without_auth(self, client):
        """Test creating item without authentication."""
        response = client.post('/api/menu', json={
            'name': 'Test Item',
            'price': 5.00,
            'category': 'food'
        })
        
        assert response.status_code == 401
    
    def test_create_menu_item_as_user(self, client, auth_headers):
        """Test creating item as regular user (should fail)."""
        response = client.post('/api/menu',
                              headers=auth_headers,
                              json={
                                  'name': 'Test Item',
                                  'price': 5.00,
                                  'category': 'food'
                              })
        
        assert response.status_code == 403
    
    def test_create_menu_item_as_staff(self, client, staff_headers):
        """Test creating item as staff (should fail - admin only)."""
        response = client.post('/api/menu',
                              headers=staff_headers,
                              json={
                                  'name': 'Test Item',
                                  'price': 5.00,
                                  'category': 'food'
                              })
        
        assert response.status_code == 403


# ==================== Update Menu Item Tests ====================

class TestUpdateMenuItem:
    """Test updating menu items (staff/admin)."""
    
    def test_update_menu_item_as_admin(self, client, admin_headers, menu_item):
        """Test updating item as admin."""
        response = client.put(f'/api/menu/{menu_item.id}',
                             headers=admin_headers,
                             json={
                                 'name': 'Updated Name',
                                 'price': 9.99
                             })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['item']['name'] == 'Updated Name'
        assert data['item']['price'] == 9.99
    
    def test_update_menu_item_as_staff(self, client, staff_headers, menu_item):
        """Test updating item as staff."""
        response = client.put(f'/api/menu/{menu_item.id}',
                             headers=staff_headers,
                             json={
                                 'name': 'Updated by Staff',
                                 'is_available': False
                             })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['item']['name'] == 'Updated by Staff'
        assert data['item']['is_available'] is False
    
    def test_update_menu_item_partial(self, client, admin_headers, menu_item):
        """Test partial update of menu item."""
        original_price = menu_item.price
        
        response = client.put(f'/api/menu/{menu_item.id}',
                             headers=admin_headers,
                             json={'name': 'New Name'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['item']['name'] == 'New Name'
        assert data['item']['price'] == original_price  # Unchanged
    
    def test_update_nonexistent_item(self, client, admin_headers):
        """Test updating non-existent item."""
        response = client.put('/api/menu/99999',
                             headers=admin_headers,
                             json={'name': 'New Name'})
        
        assert response.status_code == 404
    
    def test_update_item_invalid_price(self, client, admin_headers, menu_item):
        """Test updating with invalid price."""
        response = client.put(f'/api/menu/{menu_item.id}',
                             headers=admin_headers,
                             json={'price': -10.00})
        
        assert response.status_code == 400
    
    def test_update_item_invalid_category(self, client, admin_headers, menu_item):
        """Test updating with invalid category."""
        response = client.put(f'/api/menu/{menu_item.id}',
                             headers=admin_headers,
                             json={'category': 'invalid'})
        
        assert response.status_code == 400
    
    def test_update_item_as_user(self, client, auth_headers, menu_item):
        """Test updating as regular user (should fail)."""
        response = client.put(f'/api/menu/{menu_item.id}',
                             headers=auth_headers,
                             json={'name': 'New Name'})
        
        assert response.status_code == 403
    
    def test_update_item_without_auth(self, client, menu_item):
        """Test updating without authentication."""
        response = client.put(f'/api/menu/{menu_item.id}',
                             json={'name': 'New Name'})
        
        assert response.status_code == 401


# ==================== Delete Menu Item Tests ====================

class TestDeleteMenuItem:
    """Test deleting menu items (admin only)."""
    
    def test_delete_menu_item_success(self, client, admin_headers, menu_item):
        """Test successful item deletion."""
        response = client.delete(f'/api/menu/{menu_item.id}',
                                headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'deleted successfully' in data['message'].lower()
        
        # Verify item is deleted
        get_response = client.get(f'/api/menu/{menu_item.id}')
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_item(self, client, admin_headers):
        """Test deleting non-existent item."""
        response = client.delete('/api/menu/99999',
                                headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_delete_item_as_staff(self, client, staff_headers, menu_item):
        """Test deleting as staff (should fail)."""
        response = client.delete(f'/api/menu/{menu_item.id}',
                                headers=staff_headers)
        
        assert response.status_code == 403
    
    def test_delete_item_as_user(self, client, auth_headers, menu_item):
        """Test deleting as user (should fail)."""
        response = client.delete(f'/api/menu/{menu_item.id}',
                                headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_delete_item_without_auth(self, client, menu_item):
        """Test deleting without authentication."""
        response = client.delete(f'/api/menu/{menu_item.id}')
        
        assert response.status_code == 401


# ==================== Toggle Availability Tests ====================

class TestToggleAvailability:
    """Test toggling menu item availability."""
    
    def test_toggle_availability_as_admin(self, client, admin_headers, menu_item):
        """Test toggling availability as admin."""
        response = client.patch(f'/api/menu/{menu_item.id}/availability',
                               headers=admin_headers,
                               json={'is_available': False})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['item']['is_available'] is False
    
    def test_toggle_availability_as_staff(self, client, staff_headers, menu_item):
        """Test toggling availability as staff."""
        response = client.patch(f'/api/menu/{menu_item.id}/availability',
                               headers=staff_headers,
                               json={'is_available': False})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['item']['is_available'] is False
    
    def test_toggle_availability_missing_field(self, client, admin_headers, menu_item):
        """Test toggling without is_available field."""
        response = client.patch(f'/api/menu/{menu_item.id}/availability',
                               headers=admin_headers,
                               json={})
        
        assert response.status_code == 400
    
    def test_toggle_availability_nonexistent_item(self, client, admin_headers):
        """Test toggling non-existent item."""
        response = client.patch('/api/menu/99999/availability',
                               headers=admin_headers,
                               json={'is_available': False})
        
        assert response.status_code == 404
    
    def test_toggle_availability_as_user(self, client, auth_headers, menu_item):
        """Test toggling as regular user (should fail)."""
        response = client.patch(f'/api/menu/{menu_item.id}/availability',
                               headers=auth_headers,
                               json={'is_available': False})
        
        assert response.status_code == 403


# ==================== Integration Tests ====================

class TestMenuIntegration:
    """Test menu functionality integration."""
    
    def test_create_and_retrieve_item(self, client, admin_headers):
        """Test creating item and retrieving it."""
        # Create
        create_response = client.post('/api/menu',
                                     headers=admin_headers,
                                     json={
                                         'name': 'Integration Test',
                                         'price': 12.99,
                                         'category': 'food'
                                     })
        
        item_id = create_response.get_json()['item']['id']
        
        # Retrieve
        get_response = client.get(f'/api/menu/{item_id}')
        assert get_response.status_code == 200
        assert get_response.get_json()['name'] == 'Integration Test'
    
    def test_update_and_verify(self, client, admin_headers, menu_item):
        """Test updating item and verifying changes."""
        # Update
        client.put(f'/api/menu/{menu_item.id}',
                  headers=admin_headers,
                  json={'price': 15.99})
        
        # Verify
        response = client.get(f'/api/menu/{menu_item.id}')
        assert response.get_json()['price'] == 15.99
    
    def test_category_filtering_after_creation(self, client, admin_headers):
        """Test category filtering works after creating items."""
        # Create items in different categories
        client.post('/api/menu', headers=admin_headers, json={
            'name': 'Drink', 'price': 3.00, 'category': 'beverages'
        })
        client.post('/api/menu', headers=admin_headers, json={
            'name': 'Food', 'price': 8.00, 'category': 'food'
        })
        
        # Filter by beverages
        response = client.get('/api/menu?category=beverages')
        items = response.get_json()['items']
        assert all(item['category'] == 'beverages' for item in items)