"""
Tests for Announcement API endpoints
"""
import pytest
import json
from datetime import datetime, timezone, timedelta


class TestGetAnnouncements:
    """Test GET /api/announcements endpoint (public)"""
    
    def test_get_active_announcements(self, client, announcement):
        """Test getting active announcements without authentication"""
        response = client.get('/api/announcements')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'announcements' in data
        assert len(data['announcements']) >= 1
    
    def test_get_announcements_excludes_inactive(self, client, multiple_announcements):
        """Test inactive announcements are not returned"""
        response = client.get('/api/announcements')
        assert response.status_code == 200
        data = json.loads(response.data)
        # 3 active + 1 inactive = 4 total, should return 3
        assert len(data['announcements']) == 3
        for ann in data['announcements']:
            assert ann['is_active'] is True
    
    def test_get_announcements_excludes_expired(self, client, expired_announcement):
        """Test expired announcements are not returned"""
        response = client.get('/api/announcements')
        assert response.status_code == 200
        data = json.loads(response.data)
        # Check that expired announcement is not in results
        ids = [ann['id'] for ann in data['announcements']]
        assert expired_announcement.id not in ids
    
    def test_announcements_ordered_by_priority(self, client, multiple_announcements):
        """Test announcements are ordered by priority (high first)"""
        response = client.get('/api/announcements')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        priorities = [ann['priority'] for ann in data['announcements']]
        # High priority should come first
        assert priorities[0] == 'high'


class TestGetAllAnnouncements:
    """Test GET /api/announcements/all endpoint (admin only)"""
    
    def test_get_all_as_admin(self, client, admin_headers, multiple_announcements):
        """Test admin can get all announcements including inactive"""
        response = client.get('/api/announcements/all', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should return all 4 (3 active + 1 inactive)
        assert len(data['announcements']) == 4
    
    def test_get_all_as_user(self, client, auth_headers):
        """Test regular user cannot access all announcements"""
        response = client.get('/api/announcements/all', headers=auth_headers)
        assert response.status_code == 403
    
    def test_get_all_without_auth(self, client):
        """Test cannot access all announcements without authentication"""
        response = client.get('/api/announcements/all')
        assert response.status_code == 401


class TestGetAnnouncement:
    """Test GET /api/announcements/<id> endpoint"""
    
    def test_get_specific_announcement(self, client, announcement):
        """Test getting a specific announcement"""
        response = client.get(f'/api/announcements/{announcement.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == announcement.id
        assert data['title'] == announcement.title
    
    def test_get_nonexistent_announcement(self, client):
        """Test getting non-existent announcement"""
        response = client.get('/api/announcements/9999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestCreateAnnouncement:
    """Test POST /api/announcements endpoint"""
    
    def test_create_announcement_as_admin(self, client, admin_headers):
        """Test admin can create announcement"""
        ann_data = {
            'title': 'New Announcement',
            'message': 'This is a new announcement',
            'priority': 'high',
            'is_active': True
        }
        response = client.post(
            '/api/announcements',
            data=json.dumps(ann_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['announcement']['title'] == 'New Announcement'
        assert data['announcement']['priority'] == 'high'
    
    def test_create_announcement_with_expiry(self, client, admin_headers):
        """Test creating announcement with expiry date"""
        future_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        ann_data = {
            'title': 'Expiring Announcement',
            'message': 'This will expire',
            'priority': 'normal',
            'expires_at': future_date
        }
        response = client.post(
            '/api/announcements',
            data=json.dumps(ann_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['announcement']['expires_at'] is not None
    
    def test_create_announcement_as_user(self, client, auth_headers):
        """Test regular user cannot create announcement"""
        ann_data = {
            'title': 'New Announcement',
            'message': 'Message',
            'priority': 'normal'
        }
        response = client.post(
            '/api/announcements',
            data=json.dumps(ann_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_create_announcement_without_auth(self, client):
        """Test creating announcement without authentication"""
        ann_data = {
            'title': 'New Announcement',
            'message': 'Message'
        }
        response = client.post(
            '/api/announcements',
            data=json.dumps(ann_data),
            content_type='application/json'
        )
        assert response.status_code == 401
    
    def test_create_announcement_missing_required_fields(self, client, admin_headers):
        """Test creating announcement without required fields"""
        ann_data = {
            'title': 'No Message'
            # Missing message
        }
        response = client.post(
            '/api/announcements',
            data=json.dumps(ann_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_announcement_invalid_priority(self, client, admin_headers):
        """Test creating announcement with invalid priority"""
        ann_data = {
            'title': 'Test',
            'message': 'Message',
            'priority': 'invalid'
        }
        response = client.post(
            '/api/announcements',
            data=json.dumps(ann_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid priority' in data['error']
    
    def test_create_announcement_defaults(self, client, admin_headers):
        """Test announcement defaults are applied"""
        ann_data = {
            'title': 'Minimal Announcement',
            'message': 'Just title and message'
        }
        response = client.post(
            '/api/announcements',
            data=json.dumps(ann_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['announcement']['priority'] == 'normal'
        assert data['announcement']['is_active'] is True


class TestUpdateAnnouncement:
    """Test PUT /api/announcements/<id> endpoint"""
    
    def test_update_announcement_as_admin(self, client, admin_headers, announcement):
        """Test admin can update announcement"""
        update_data = {
            'title': 'Updated Title',
            'priority': 'high'
        }
        response = client.put(
            f'/api/announcements/{announcement.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['announcement']['title'] == 'Updated Title'
        assert data['announcement']['priority'] == 'high'
    
    def test_update_announcement_deactivate(self, client, admin_headers, announcement):
        """Test deactivating an announcement"""
        update_data = {'is_active': False}
        response = client.put(
            f'/api/announcements/{announcement.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['announcement']['is_active'] is False
    
    def test_update_announcement_expiry(self, client, admin_headers, announcement):
        """Test updating announcement expiry date"""
        future_date = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
        update_data = {'expires_at': future_date}
        response = client.put(
            f'/api/announcements/{announcement.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['announcement']['expires_at'] is not None
    
    def test_update_announcement_remove_expiry(self, client, admin_headers, announcement):
        """Test removing expiry date from announcement"""
        update_data = {'expires_at': None}
        response = client.put(
            f'/api/announcements/{announcement.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['announcement']['expires_at'] is None
    
    def test_update_announcement_as_user(self, client, auth_headers, announcement):
        """Test regular user cannot update announcement"""
        update_data = {'title': 'Hacked'}
        response = client.put(
            f'/api/announcements/{announcement.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_update_nonexistent_announcement(self, client, admin_headers):
        """Test updating non-existent announcement"""
        update_data = {'title': 'Updated'}
        response = client.put(
            '/api/announcements/9999',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 404
    
    def test_update_announcement_invalid_priority(self, client, admin_headers, announcement):
        """Test updating with invalid priority"""
        update_data = {'priority': 'invalid'}
        response = client.put(
            f'/api/announcements/{announcement.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400


class TestDeleteAnnouncement:
    """Test DELETE /api/announcements/<id> endpoint"""
    
    def test_delete_announcement_as_admin(self, client, admin_headers, announcement):
        """Test admin can delete announcement"""
        response = client.delete(
            f'/api/announcements/{announcement.id}',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message']
        
        # Verify announcement is deleted
        get_response = client.get(f'/api/announcements/{announcement.id}')
        assert get_response.status_code == 404
    
    def test_delete_announcement_as_staff(self, client, staff_headers, announcement):
        """Test staff cannot delete announcement"""
        response = client.delete(
            f'/api/announcements/{announcement.id}',
            headers=staff_headers
        )
        assert response.status_code == 403
    
    def test_delete_announcement_as_user(self, client, auth_headers, announcement):
        """Test regular user cannot delete announcement"""
        response = client.delete(
            f'/api/announcements/{announcement.id}',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_delete_nonexistent_announcement(self, client, admin_headers):
        """Test deleting non-existent announcement"""
        response = client.delete(
            '/api/announcements/9999',
            headers=admin_headers
        )
        assert response.status_code == 404