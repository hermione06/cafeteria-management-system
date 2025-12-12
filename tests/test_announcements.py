import pytest
import json
from models import db, Announcement

# Using the common fixtures from test_auth.py for brevity (app, client, init_db, auth_headers)

@pytest.fixture
def sample_announcement(init_db):
    """Creates a sample announcement."""
    announcement = Announcement(
        title='System Maintenance',
        message='The system will be down tonight.',
        priority='high'
    )
    db.session.add(announcement)
    db.session.commit()
    return announcement

# --- Announcement API Tests ---

def test_get_announcements_unauthenticated(client, sample_announcement):
    """Everyone can view announcements."""
    response = client.get('/api/announcements')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['announcements']) == 1
    assert data['announcements'][0]['title'] == 'System Maintenance'

def test_create_announcement_admin_success(client, auth_headers):
    """Admin can create a new announcement."""
    new_announcement_data = {
        'title': 'New Menu Item',
        'message': 'Try our new special!',
        'priority': 'normal'
    }
    response = client.post('/api/announcements', json=new_announcement_data, headers=auth_headers['admin'])
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['announcement']['title'] == 'New Menu Item'
    assert Announcement.query.count() == 1 

def test_create_announcement_student_forbidden(client, auth_headers):
    """Students cannot create announcements."""
    response = client.post('/api/announcements', json={'title': 'a', 'message': 'm'}, headers=auth_headers['student'])
    assert response.status_code == 403
    
def test_create_announcement_staff_forbidden(client, auth_headers):
    """Staff cannot create announcements (assuming only Admin can)."""
    response = client.post('/api/announcements', json={'title': 'a', 'message': 'm'}, headers=auth_headers['staff'])
    assert response.status_code == 403

def test_update_announcement_admin_success(client, auth_headers, sample_announcement):
    """Admin can update an existing announcement."""
    update_data = {
        'title': 'Maintenance Postponed',
        'priority': 'low'
    }
    response = client.put(f'/api/announcements/{sample_announcement.id}', json=update_data, headers=auth_headers['admin'])
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['announcement']['title'] == 'Maintenance Postponed'
    assert data['announcement']['priority'] == 'low'

def test_delete_announcement_admin_success(client, auth_headers, sample_announcement):
    """Admin can delete an announcement."""
    announcement_id = sample_announcement.id
    
    response = client.delete(f'/api/announcements/{announcement_id}', headers=auth_headers['admin'])
    assert response.status_code == 204
    
    # Verify deletion
    assert Announcement.query.get(announcement_id) is None