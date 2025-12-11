"""
Comprehensive tests for order management endpoints.
Testing order creation, updates, status management, and authorization.
"""
import pytest


# ==================== Get Orders Tests ====================

class TestGetOrders:
    """Test retrieving orders."""
    
    def test_get_user_orders(self, client, auth_headers, order):
        """Test user getting their own orders."""
        response = client.get('/api/orders', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'orders' in data
        assert len(data['orders']) >= 1
        assert all(o['user_id'] == order.user_id for o in data['orders'])
    
    def test_get_all_orders_as_admin(self, client, admin_headers, order):
        """Test admin getting all orders."""
        response = client.get('/api/orders', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'orders' in data
    
    def test_get_all_orders_as_staff(self, client, staff_headers, order):
        """Test staff getting all orders."""
        response = client.get('/api/orders', headers=staff_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'orders' in data
    
    def test_get_orders_filter_by_status(self, client, auth_headers, order):
        """Test filtering orders by status."""
        response = client.get('/api/orders?status=pending', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert all(o['status'] == 'pending' for o in data['orders'])
    
    def test_get_orders_filter_by_payment(self, client, auth_headers, order):
        """Test filtering orders by payment status."""
        response = client.get('/api/orders?is_paid=false', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert all(o['is_paid'] is False for o in data['orders'])
    
    def test_get_orders_admin_filter_by_user(self, client, admin_headers, user, order):
        """Test admin filtering orders by user."""
        response = client.get(f'/api/orders?user_id={user.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert all(o['user_id'] == user.id for o in data['orders'])
    
    def test_get_orders_pagination(self, client, auth_headers, order):
        """Test order pagination."""
        response = client.get('/api/orders?page=1&per_page=5', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'pagination' in data
        assert len(data['orders']) <= 5
    
    def test_get_orders_without_auth(self, client):
        """Test getting orders without authentication."""
        response = client.get('/api/orders')
        
        assert response.status_code == 401


# ==================== Get Single Order Tests ====================

class TestGetOrder:
    """Test retrieving single order."""
    
    def test_get_own_order(self, client, auth_headers, order):
        """Test user getting their own order."""
        response = client.get(f'/api/orders/{order.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == order.id
        assert 'items' in data
        assert 'total_price' in data
    
    def test_get_other_user_order(self, client, user, order, app):
        """Test user trying to get another user's order."""
        # Create another user
        with app.app_context():
            from models import User, db
            other_user = User(username='otheruser', email='other@test.com')
            other_user.set_password('TestPass123')
            other_user.is_verified = True
            db.session.add(other_user)
            db.session.commit()
        
        # Login as other user
        login_response = client.post('/api/auth/login', json={
            'username': 'otheruser',
            'password': 'TestPass123'
        })
        other_token = login_response.get_json()['access_token']
        other_headers = {'Authorization': f'Bearer {other_token}'}
        
        # Try to get first user's order
        response = client.get(f'/api/orders/{order.id}', headers=other_headers)
        assert response.status_code == 403
    
    def test_get_order_as_admin(self, client, admin_headers, order):
        """Test admin getting any order."""
        response = client.get(f'/api/orders/{order.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == order.id
        assert 'user' in data  # Admin should see user info
    
    def test_get_order_as_staff(self, client, staff_headers, order):
        """Test staff getting any order."""
        response = client.get(f'/api/orders/{order.id}', headers=staff_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == order.id
    
    def test_get_nonexistent_order(self, client, auth_headers):
        """Test getting non-existent order."""
        response = client.get('/api/orders/99999', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'not found' in data['error'].lower()


# ==================== Create Order Tests ====================

class TestCreateOrder:
    """Test creating orders."""
    
    def test_create_order_success(self, client, auth_headers, menu_items):
        """Test successful order creation."""
        response = client.post('/api/orders',
                              headers=auth_headers,
                              json={
                                  'items': [
                                      {'menu_item_id': menu_items[0].id, 'quantity': 2},
                                      {'menu_item_id': menu_items[1].id, 'quantity': 1}
                                  ]
                              })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'order' in data
        assert data['order']['status'] == 'pending'
        assert len(data['order']['items']) == 2
    
    def test_create_order_with_special_instructions(self, client, auth_headers, menu_items):
        """Test creating order with special instructions."""
        response = client.post('/api/orders',
                              headers=auth_headers,
                              json={
                                  'items': [
                                      {'menu_item_id': menu_items[0].id, 'quantity': 1}
                                  ],
                                  'special_instructions': 'No sugar please'
                              })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['order']['special_instructions'] == 'No sugar please'
    
    def test_create_order_empty_items(self, client, auth_headers):
        """Test creating order with no items."""
        response = client.post('/api/orders',
                              headers=auth_headers,
                              json={'items': []})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_create_order_missing_items(self, client, auth_headers):
        """Test creating order without items field."""
        response = client.post('/api/orders',
                              headers=auth_headers,
                              json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_create_order_invalid_menu_item(self, client, auth_headers):
        """Test creating order with non-existent menu item."""
        response = client.post('/api/orders',
                              headers=auth_headers,
                              json={
                                  'items': [
                                      {'menu_item_id': 99999, 'quantity': 1}
                                  ]
                              })
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'not found' in data['error'].lower()
    
    def test_create_order_unavailable_item(self, client, auth_headers, menu_items):
        """Test creating order with unavailable item."""
        # menu_items[4] is unavailable
        response = client.post('/api/orders',
                              headers=auth_headers,
                              json={
                                  'items': [
                                      {'menu_item_id': menu_items[4].id, 'quantity': 1}
                                  ]
                              })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'unavailable' in data['error'].lower()
    
    def test_create_order_invalid_quantity(self, client, auth_headers, menu_items):
        """Test creating order with invalid quantity."""
        response = client.post('/api/orders',
                              headers=auth_headers,
                              json={
                                  'items': [
                                      {'menu_item_id': menu_items[0].id, 'quantity': 0}
                                  ]
                              })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'positive' in data['error'].lower()
    
    def test_create_order_missing_quantity(self, client, auth_headers, menu_items):
        """Test creating order without quantity."""
        response = client.post('/api/orders',
                              headers=auth_headers,
                              json={
                                  'items': [
                                      {'menu_item_id': menu_items[0].id}
                                  ]
                              })
        
        assert response.status_code == 400
    
    def test_create_order_without_auth(self, client, menu_items):
        """Test creating order without authentication."""
        response = client.post('/api/orders', json={
            'items': [
                {'menu_item_id': menu_items[0].id, 'quantity': 1}
            ]
        })
        
        assert response.status_code == 401


# ==================== Add/Remove Order Items Tests ====================

class TestModifyOrderItems:
    """Test adding and removing items from orders."""
    
    def test_add_item_to_order(self, client, auth_headers, order, menu_items):
        """Test adding item to existing order."""
        response = client.post(f'/api/orders/{order.id}/items',
                              headers=auth_headers,
                              json={
                                  'menu_item_id': menu_items[3].id,
                                  'quantity': 2
                              })
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['order']['items']) > 2
    
    def test_add_existing_item_increments_quantity(self, client, auth_headers, order, menu_items):
        """Test adding existing item increments quantity."""
        # Get original quantity
        get_response = client.get(f'/api/orders/{order.id}', headers=auth_headers)
        original_items = get_response.get_json()['items']
        original_item = next(i for i in original_items if i['menu_item_id'] == menu_items[0].id)
        original_quantity = original_item['quantity']
        
        # Add more of the same item
        client.post(f'/api/orders/{order.id}/items',
                   headers=auth_headers,
                   json={
                       'menu_item_id': menu_items[0].id,
                       'quantity': 3
                   })
        
        # Verify quantity increased
        get_response = client.get(f'/api/orders/{order.id}', headers=auth_headers)
        updated_items = get_response.get_json()['items']
        updated_item = next(i for i in updated_items if i['menu_item_id'] == menu_items[0].id)
        assert updated_item['quantity'] == original_quantity + 3
    
    def test_add_item_to_non_pending_order(self, client, auth_headers, completed_order, menu_items):
        """Test adding item to non-pending order."""
        response = client.post(f'/api/orders/{completed_order.id}/items',
                              headers=auth_headers,
                              json={
                                  'menu_item_id': menu_items[0].id,
                                  'quantity': 1
                              })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'pending' in data['error'].lower()
    
    def test_remove_item_from_order(self, client, auth_headers, order):
        """Test removing item from order."""
        # Get an item ID from the order
        get_response = client.get(f'/api/orders/{order.id}', headers=auth_headers)
        item_id = get_response.get_json()['items'][0]['id']
        
        response = client.delete(f'/api/orders/{order.id}/items/{item_id}',
                                headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['order']['items']) < 2
    
    def test_remove_item_from_non_pending_order(self, client, auth_headers, completed_order):
        """Test removing item from non-pending order."""
        # Get an item ID
        get_response = client.get(f'/api/orders/{completed_order.id}', headers=auth_headers)
        item_id = get_response.get_json()['items'][0]['id']
        
        response = client.delete(f'/api/orders/{completed_order.id}/items/{item_id}',
                                headers=auth_headers)
        
        assert response.status_code == 400


# ==================== Update Order Status Tests ====================

class TestUpdateOrderStatus:
    """Test updating order status (staff/admin)."""
    
    def test_update_status_as_staff(self, client, staff_headers, order):
        """Test staff updating order status."""
        response = client.patch(f'/api/orders/{order.id}/status',
                               headers=staff_headers,
                               json={'status': 'confirmed'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['order']['status'] == 'confirmed'
    
    def test_update_status_as_admin(self, client, admin_headers, order):
        """Test admin updating order status."""
        response = client.patch(f'/api/orders/{order.id}/status',
                               headers=admin_headers,
                               json={'status': 'preparing'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['order']['status'] == 'preparing'
    
    def test_update_status_to_completed(self, client, admin_headers, order):
        """Test marking order as completed."""
        response = client.patch(f'/api/orders/{order.id}/status',
                               headers=admin_headers,
                               json={'status': 'completed'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['order']['status'] == 'completed'
        assert data['order']['completed_at'] is not None
    
    def test_update_status_with_admin_notes(self, client, admin_headers, order):
        """Test updating status with admin notes."""
        response = client.patch(f'/api/orders/{order.id}/status',
                               headers=admin_headers,
                               json={
                                   'status': 'ready',
                                   'admin_notes': 'Ready for pickup at counter 3'
                               })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['order']['admin_notes'] == 'Ready for pickup at counter 3'
    
    def test_update_status_invalid_value(self, client, admin_headers, order):
        """Test updating with invalid status."""
        response = client.patch(f'/api/orders/{order.id}/status',
                               headers=admin_headers,
                               json={'status': 'invalid_status'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'invalid' in data['error'].lower()
    
    def test_update_status_as_user(self, client, auth_headers, order):
        """Test user trying to update status (should fail)."""
        response = client.patch(f'/api/orders/{order.id}/status',
                               headers=auth_headers,
                               json={'status': 'completed'})
        
        assert response.status_code == 403
    
    def test_update_status_nonexistent_order(self, client, admin_headers):
        """Test updating status of non-existent order."""
        response = client.patch('/api/orders/99999/status',
                               headers=admin_headers,
                               json={'status': 'completed'})
        
        assert response.status_code == 404


# ==================== Update Payment Status Tests ====================

class TestUpdatePaymentStatus:
    """Test updating order payment status (staff/admin)."""
    
    def test_mark_order_paid(self, client, admin_headers, order):
        """Test marking order as paid."""
        response = client.patch(f'/api/orders/{order.id}/payment',
                               headers=admin_headers,
                               json={
                                   'is_paid': True,
                                   'payment_method': 'cash'
                               })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['order']['is_paid'] is True
        assert data['order']['payment_method'] == 'cash'
    
    def test_mark_order_unpaid(self, client, admin_headers, completed_order):
        """Test marking paid order as unpaid."""
        response = client.patch(f'/api/orders/{completed_order.id}/payment',
                               headers=admin_headers,
                               json={'is_paid': False})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['order']['is_paid'] is False
    
    def test_update_payment_as_staff(self, client, staff_headers, order):
        """Test staff updating payment status."""
        response = client.patch(f'/api/orders/{order.id}/payment',
                               headers=staff_headers,
                               json={'is_paid': True})
        
        assert response.status_code == 200
    
    def test_update_payment_as_user(self, client, auth_headers, order):
        """Test user trying to update payment (should fail)."""
        response = client.patch(f'/api/orders/{order.id}/payment',
                               headers=auth_headers,
                               json={'is_paid': True})
        
        assert response.status_code == 403


# ==================== Delete Order Tests ====================

class TestDeleteOrder:
    """Test deleting orders."""
    
    def test_delete_own_pending_order(self, client, auth_headers, order):
        """Test user deleting their own pending order."""
        response = client.delete(f'/api/orders/{order.id}',
                                headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'deleted successfully' in data['message'].lower()
        
        # Verify deleted
        get_response = client.get(f'/api/orders/{order.id}', headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_completed_order_as_user(self, client, auth_headers, completed_order):
        """Test user trying to delete completed order (should fail)."""
        response = client.delete(f'/api/orders/{completed_order.id}',
                                headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'pending' in data['error'].lower()
    
    def test_delete_any_order_as_admin(self, client, admin_headers, completed_order):
        """Test admin deleting any order."""
        response = client.delete(f'/api/orders/{completed_order.id}',
                                headers=admin_headers)
        
        assert response.status_code == 200
    
    def test_delete_other_user_order(self, client, auth_headers, order, app):
        """Test user trying to delete another user's order."""
        # Create another user
        with app.app_context():
            from models import User, db
            other_user = User(username='otheruser2', email='other2@test.com')
            other_user.set_password('TestPass123')
            other_user.is_verified = True
            db.session.add(other_user)
            db.session.commit()
        
        # Login as other user
        login_response = client.post('/api/auth/login', json={
            'username': 'otheruser2',
            'password': 'TestPass123'
        })
        other_token = login_response.get_json()['access_token']
        other_headers = {'Authorization': f'Bearer {other_token}'}
        
        # Try to delete first user's order
        response = client.delete(f'/api/orders/{order.id}', headers=other_headers)
        assert response.status_code == 403


# ==================== Integration Tests ====================

class TestOrderIntegration:
    """Test order functionality integration."""
    
    def test_complete_order_workflow(self, client, auth_headers, admin_headers, menu_items):
        """Test complete order workflow from creation to completion."""
        # 1. Create order
        create_response = client.post('/api/orders',
                                     headers=auth_headers,
                                     json={
                                         'items': [
                                             {'menu_item_id': menu_items[0].id, 'quantity': 2}
                                         ]
                                     })
        order_id = create_response.get_json()['order']['id']
        
        # 2. Update status to confirmed
        client.patch(f'/api/orders/{order_id}/status',
                    headers=admin_headers,
                    json={'status': 'confirmed'})
        
        # 3. Update to preparing
        client.patch(f'/api/orders/{order_id}/status',
                    headers=admin_headers,
                    json={'status': 'preparing'})
        
        # 4. Update to ready
        client.patch(f'/api/orders/{order_id}/status',
                    headers=admin_headers,
                    json={'status': 'ready'})
        
        # 5. Mark as paid
        client.patch(f'/api/orders/{order_id}/payment',
                    headers=admin_headers,
                    json={'is_paid': True, 'payment_method': 'card'})
        
        # 6. Complete order
        complete_response = client.patch(f'/api/orders/{order_id}/status',
                                        headers=admin_headers,
                                        json={'status': 'completed'})
        
        assert complete_response.status_code == 200
        final_order = complete_response.get_json()['order']
        assert final_order['status'] == 'completed'
        assert final_order['is_paid'] is True
        assert final_order['completed_at'] is not None
    
    def test_order_total_calculation(self, client, auth_headers, menu_items):
        """Test order total is calculated correctly."""
        response = client.post('/api/orders',
                              headers=auth_headers,
                              json={
                                  'items': [
                                      {'menu_item_id': menu_items[0].id, 'quantity': 2},  # 2.50 * 2 = 5.00
                                      {'menu_item_id': menu_items[1].id, 'quantity': 1},  # 3.50 * 1 = 3.50
                                  ]
                              })
        
        order = response.get_json()['order']
        expected_total = (menu_items[0].price * 2) + (menu_items[1].price * 1)
        assert order['total_price'] == pytest.approx(expected_total, 0.01)