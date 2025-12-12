from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Announcement
from src.utils.decorators import admin_required
from datetime import datetime, timezone

announcement_bp = Blueprint('announcements', __name__)


@announcement_bp.route('', methods=['GET'])
def get_announcements():
    """Get all active announcements (public endpoint)"""
    try:
        # Get only active, non-expired announcements
        now = datetime.now(timezone.utc)
        
        announcements = Announcement.query.filter(
            Announcement.is_active == True,
            db.or_(
                Announcement.expires_at.is_(None),
                Announcement.expires_at > now
            )
        ).order_by(
            Announcement.priority.desc(),
            Announcement.created_at.desc()
        ).all()
        
        return jsonify({
            "announcements": [ann.to_dict() for ann in announcements]
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch announcements: {str(e)}"}), 500


@announcement_bp.route('/all', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_announcements():
    """Get all announcements including inactive (Admin only)"""
    try:
        announcements = Announcement.query.order_by(
            Announcement.created_at.desc()
        ).all()
        
        return jsonify({
            "announcements": [ann.to_dict() for ann in announcements]
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch announcements: {str(e)}"}), 500


@announcement_bp.route('/<int:announcement_id>', methods=['GET'])
def get_announcement(announcement_id):
    """Get a specific announcement"""
    try:
        announcement = db.session.get(Announcement, announcement_id)
        
        if not announcement:
            return jsonify({"error": "Announcement not found"}), 404
        
        return jsonify(announcement.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch announcement: {str(e)}"}), 500


@announcement_bp.route('', methods=['POST'])
@jwt_required()
@admin_required()
def create_announcement():
    """Create a new announcement (Admin only)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('title') or not data.get('message'):
            return jsonify({"error": "Title and message are required"}), 400
        
        # Validate priority
        priority = data.get('priority', 'normal')
        if priority not in ['low', 'normal', 'high']:
            return jsonify({"error": "Invalid priority. Must be: low, normal, or high"}), 400
        
        # Parse expiry date if provided
        expires_at = None
        if 'expires_at' in data and data['expires_at']:
            try:
                expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid expires_at format. Use ISO format"}), 400
        
        # Create announcement
        announcement = Announcement(
            title=data['title'],
            message=data['message'],
            priority=priority,
            is_active=data.get('is_active', True),
            created_by=user_id,
            expires_at=expires_at
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify({
            "message": "Announcement created successfully",
            "announcement": announcement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create announcement: {str(e)}"}), 500


@announcement_bp.route('/<int:announcement_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_announcement(announcement_id):
    """Update an announcement (Admin only)"""
    try:
        announcement = db.session.get(Announcement, announcement_id)
        
        if not announcement:
            return jsonify({"error": "Announcement not found"}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            announcement.title = data['title']
        
        if 'message' in data:
            announcement.message = data['message']
        
        if 'priority' in data:
            if data['priority'] not in ['low', 'normal', 'high']:
                return jsonify({"error": "Invalid priority"}), 400
            announcement.priority = data['priority']
        
        if 'is_active' in data:
            announcement.is_active = bool(data['is_active'])
        
        if 'expires_at' in data:
            if data['expires_at']:
                try:
                    announcement.expires_at = datetime.fromisoformat(
                        data['expires_at'].replace('Z', '+00:00')
                    )
                except ValueError:
                    return jsonify({"error": "Invalid expires_at format"}), 400
            else:
                announcement.expires_at = None
        
        db.session.commit()
        
        return jsonify({
            "message": "Announcement updated successfully",
            "announcement": announcement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update announcement: {str(e)}"}), 500


@announcement_bp.route('/<int:announcement_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_announcement(announcement_id):
    """Delete an announcement (Admin only)"""
    try:
        announcement = db.session.get(Announcement, announcement_id)
        
        if not announcement:
            return jsonify({"error": "Announcement not found"}), 404
        
        db.session.delete(announcement)
        db.session.commit()
        
        return jsonify({"message": "Announcement deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete announcement: {str(e)}"}), 500