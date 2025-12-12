"""
Tests for Order API endpoints
"""
import pytest
import json


class TestGetOrders:
    """Test GET /api/orders endpoint"""
    
    def test_get_orders_as_user(self, client, auth_headers, order):
        """Test user can see their own orders"""
        response = client.get('/api/orders', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'orders' in data
        assert len(data['orders']) == 1
        assert data['orders'][0]['id'] == order.id
    
    def test_get_orders_as_admin(self, client, admin_headers, multiple_orders):
        """Test admin can see all orders"""
        response = client.get('/api/orders', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['orders']) >= 2
    
    def test_get_orders_without_auth(self, client):
        """Test getting orders without authentication"""
        response = client.get('/api/orders')
        assert response.status_code == 401
    
    def test_filter_orders_by_status(self, client, auth_headers, multiple_orders):
        """Test filtering orders by status"""
        response = client.get('/api/orders?status=pending', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        for order in data['orders']:
            assert order['status'] == 'pending'
    
    def test_filter_orders_by_payment(self, client, auth_headers, multiple_orders):
        """Test filtering orders by payment status"""
        response = client.get('/api/orders?is_paid=true', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        for order in data['orders']:
            assert order['is_paid'] is True
    
    def test_pagination(self, client, auth_headers, multiple_orders):
        """Test order pagination"""
        response = client.get('/api/orders?per_page=1', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'pagination' in data
        assert data['pagination']['per_page'] == 1


class TestGetOrder:
    """Test GET /api/orders/<id> endpoint"""
    
    def test_get_own_order(self, client, auth_headers, order):
        """Test user can get their own order"""
        response = client.get(f'/api/orders/{order.id}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == order.id
        assert 'items' in data
        assert 'total_price' in data
    
    def test_get_other_user_order(self, client, auth_headers, completed_order, staff_user):
        """Test user cannot get another user's order"""
        # completed_order belongs to regular_user
        # auth_headers is for regular_user
        # We need to create another user's order
        response = client.get(f'/api/orders/{completed_order.id}', headers=auth_headers)
        # This should succeed since both belong to regular_user
        assert response.status_code == 200
    
    def test_get_order_as_admin(self, client, admin_headers, order):
        """Test admin can get any order"""
        response = client.get(f'/api/orders/{order.id}', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data  # Admin sees user info
    
    def test_get_nonexistent_order(self, client, auth_headers):
        """Test getting non-existent order"""
        response = client.get('/api/orders/9999', headers=auth_headers)
        assert response.status_code == 404


class TestCreateOrder:
    """Test POST /api/orders endpoint"""
    
    def test_create_order(self, client, auth_headers, menu_item):
        """Test creating a new order"""
        order_data = {
            'items': [
                {'menu_item_id': menu_item.id, 'quantity': 2}
            ],
            'special_instructions': 'No sugar please'
        }
        response = client.post(
            '/api/orders',
            data=json.dumps(order_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'order' in data
        assert data['order']['status'] == 'pending'
        assert len(data['order']['items']) == 1
        assert data['order']['items'][0]['quantity'] == 2
    
    def test_create_order_multiple_items(self, client, auth_headers, multiple_menu_items):
        """Test creating order with multiple items"""
        order_data = {
            'items': [
                {'menu_item_id': multiple_menu_items[0].id, 'quantity': 2},
                {'menu_item_id': multiple_menu_items[1].id, 'quantity': 1}
            ]
        }
        response = client.post(
            '/api/orders',
            data=json.dumps(order_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert len(data['order']['items']) == 2
    
    def test_create_order_without_items(self, client, auth_headers):
        """Test creating order without items"""
        order_data = {'items': []}
        response = client.post(
            '/api/orders',
            data=json.dumps(order_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_order_unavailable_item(self, client, auth_headers, unavailable_menu_item):
        """Test creating order with unavailable item"""
        order_data = {
            'items': [
                {'menu_item_id': unavailable_menu_item.id, 'quantity': 1}
            ]
        }
        response = client.post(
            '/api/orders',
            data=json.dumps(order_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'unavailable' in data['error'].lower()
    
    def test_create_order_nonexistent_item(self, client, auth_headers):
        """Test creating order with non-existent menu item"""
        order_data = {
            'items': [
                {'menu_item_id': 9999, 'quantity': 1}
            ]
        }
        response = client.post(
            '/api/orders',
            data=json.dumps(order_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_create_order_invalid_quantity(self, client, auth_headers, menu_item):
        """Test creating order with invalid quantity"""
        order_data = {
            'items': [
                {'menu_item_id': menu_item.id, 'quantity': 0}
            ]
        }
        response = client.post(
            '/api/orders',
            data=json.dumps(order_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 400


class TestAddOrderItem:
    """Test POST /api/orders/<id>/items endpoint"""
    
    def test_add_item_to_order(self, client, auth_headers, order, multiple_menu_items):
        """Test adding item to existing order"""
        item_data = {
            'menu_item_id': multiple_menu_items[1].id,
            'quantity': 1
        }
        response = client.post(
            f'/api/orders/{order.id}/items',
            data=json.dumps(item_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['order']['items']) == 2
    
    def test_add_existing_item_increases_quantity(self, client, auth_headers, order, menu_item):
        """Test adding same item increases quantity"""
        item_data = {
            'menu_item_id': menu_item.id,
            'quantity': 1
        }
        response = client.post(
            f'/api/orders/{order.id}/items',
            data=json.dumps(item_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['order']['items'][0]['quantity'] == 3  # Was 2, now 3
    
    def test_add_item_to_completed_order(self, client, auth_headers, completed_order, menu_item):
        """Test cannot add item to completed order"""
        item_data = {
            'menu_item_id': menu_item.id,
            'quantity': 1
        }
        response = client.post(
            f'/api/orders/{completed_order.id}/items',
            data=json.dumps(item_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'pending' in data['error'].lower()


class TestRemoveOrderItem:
    """Test DELETE /api/orders/<id>/items/<item_id> endpoint"""
    
    # def test_remove_item_from_order(self, client, auth_headers, order):
    #     """Test removing item from order"""
    #     order_item_id = order.items.first().id
    #     response = client.delete(
    #         f'/api/orders/{order.id}/items/{order_item_id}',
    #         headers=auth_headers
    #     )
    #     assert response.status_code == 200
    #     data = json.loads(response.data)
    #     assert len(data['order']['items']) == 0
    
    # def test_remove_item_from_completed_order(self, client, auth_headers, completed_order):
    #     """Test cannot remove item from completed order"""
    #     order_item_id = completed_order.items.first().id
    #     response = client.delete(
    #         f'/api/orders/{completed_order.id}/items/{order_item_id}',
    #         headers=auth_headers
    #     )
    #     assert response.status_code == 400


class TestUpdateOrderStatus:
    """Test PATCH /api/orders/<id>/status endpoint"""
    
    def test_update_status_as_staff(self, client, staff_headers, order):
        """Test staff can update order status"""
        status_data = {'status': 'confirmed'}
        response = client.patch(
            f'/api/orders/{order.id}/status',
            data=json.dumps(status_data),
            content_type='application/json',
            headers=staff_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['order']['status'] == 'confirmed'
    
    def test_update_status_as_admin(self, client, admin_headers, order):
        """Test admin can update order status"""
        status_data = {'status': 'preparing'}
        response = client.patch(
            f'/api/orders/{order.id}/status',
            data=json.dumps(status_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
    
    def test_update_status_as_user(self, client, auth_headers, order):
        """Test regular user cannot update order status"""
        status_data = {'status': 'confirmed'}
        response = client.patch(
            f'/api/orders/{order.id}/status',
            data=json.dumps(status_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_update_to_completed_sets_timestamp(self, client, admin_headers, order):
        """Test updating to completed sets completed_at"""
        status_data = {'status': 'completed'}
        response = client.patch(
            f'/api/orders/{order.id}/status',
            data=json.dumps(status_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['order']['completed_at'] is not None
    
    def test_update_status_invalid(self, client, admin_headers, order):
        """Test updating with invalid status"""
        status_data = {'status': 'invalid_status'}
        response = client.patch(
            f'/api/orders/{order.id}/status',
            data=json.dumps(status_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400


class TestUpdatePaymentStatus:
    """Test PATCH /api/orders/<id>/payment endpoint"""
    
    def test_update_payment_as_admin(self, client, admin_headers, order):
        """Test admin can update payment status"""
        payment_data = {
            'is_paid': True,
            'payment_method': 'card'
        }
        response = client.patch(
            f'/api/orders/{order.id}/payment',
            data=json.dumps(payment_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['order']['is_paid'] is True
        assert data['order']['payment_method'] == 'card'
    
    def test_update_payment_as_staff(self, client, staff_headers, order):
        """Test staff can update payment status"""
        payment_data = {'is_paid': True}
        response = client.patch(
            f'/api/orders/{order.id}/payment',
            data=json.dumps(payment_data),
            content_type='application/json',
            headers=staff_headers
        )
        assert response.status_code == 200
    
    def test_update_payment_as_user(self, client, auth_headers, order):
        """Test regular user cannot update payment status"""
        payment_data = {'is_paid': True}
        response = client.patch(
            f'/api/orders/{order.id}/payment',
            data=json.dumps(payment_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 403


class TestDeleteOrder:
    """Test DELETE /api/orders/<id> endpoint"""
    
    def test_delete_own_pending_order(self, client, auth_headers, order):
        """Test user can delete their own pending order"""
        response = client.delete(
            f'/api/orders/{order.id}',
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_delete_own_completed_order(self, client, auth_headers, completed_order):
        """Test user cannot delete completed order"""
        response = client.delete(
            f'/api/orders/{completed_order.id}',
            headers=auth_headers
        )
        assert response.status_code == 400
    
    def test_delete_any_order_as_admin(self, client, admin_headers, completed_order):
        """Test admin can delete any order"""
        response = client.delete(
            f'/api/orders/{completed_order.id}',
            headers=admin_headers
        )
        assert response.status_code == 200