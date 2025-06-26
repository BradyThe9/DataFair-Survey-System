from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.database import db
from app.models import Activity

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/activities', methods=['GET'])
@login_required
def get_activities():
    """Get user's activity feed"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        activity_type = request.args.get('type', None)
        
        # Build query
        query = Activity.query.filter_by(user_id=current_user.id)
        
        # Filter by type if specified
        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        
        # Get activities with pagination
        activities = query.order_by(Activity.created_at.desc())\
                          .offset(offset)\
                          .limit(limit)\
                          .all()
        
        # Convert to dict
        activities_data = [activity.to_dict() for activity in activities]
        
        return jsonify({
            'success': True,
            'activities': activities_data,
            'total': query.count()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/activities/<int:activity_id>', methods=['GET'])
@login_required
def get_activity(activity_id):
    """Get a specific activity"""
    try:
        activity = Activity.query.filter_by(
            id=activity_id,
            user_id=current_user.id
        ).first()
        
        if not activity:
            return jsonify({'error': 'Activity not found'}), 404
            
        return jsonify({
            'success': True,
            'activity': activity.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/activities/stats', methods=['GET'])
@login_required
def get_activity_stats():
    """Get activity statistics"""
    try:
        # Total activities
        total_activities = Activity.query.filter_by(user_id=current_user.id).count()
        
        # Activities this month
        current_month = datetime.now().month
        current_year = datetime.now().year
        this_month = Activity.query.filter(
            Activity.user_id == current_user.id,
            db.extract('month', Activity.created_at) == current_month,
            db.extract('year', Activity.created_at) == current_year
        ).count()
        
        # Activities by type
        activity_types = db.session.query(
            Activity.activity_type,
            db.func.count(Activity.id).label('count')
        ).filter_by(user_id=current_user.id)\
         .group_by(Activity.activity_type)\
         .all()
        
        type_stats = {activity_type: count for activity_type, count in activity_types}
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_count = Activity.query.filter(
            Activity.user_id == current_user.id,
            Activity.created_at >= week_ago
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total_activities,
                'thisMonth': this_month,
                'thisWeek': recent_count,
                'byType': type_stats
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/activities', methods=['POST'])
@login_required
def create_activity():
    """Create a new activity (for testing or manual entries)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Required fields
        title = data.get('title')
        description = data.get('description')
        
        if not title or not description:
            return jsonify({'error': 'Title and description are required'}), 400
            
        # Optional fields
        activity_type = data.get('type', 'manual')
        earning = float(data.get('earning', 0.0))
        company = data.get('company', 'DataFair')
        
        # Create activity
        activity = Activity(
            user_id=current_user.id,
            title=title,
            description=description,
            activity_type=activity_type,
            earning=earning,
            company=company
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Activity created successfully',
            'activity': activity.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/activities/bulk-delete', methods=['DELETE'])
@login_required
def bulk_delete_activities():
    """Delete multiple activities (for cleanup)"""
    try:
        data = request.get_json()
        activity_ids = data.get('activity_ids', [])
        
        if not activity_ids:
            return jsonify({'error': 'No activity IDs provided'}), 400
            
        # Delete activities that belong to the current user
        deleted_count = Activity.query.filter(
            Activity.id.in_(activity_ids),
            Activity.user_id == current_user.id
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count} activities deleted',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500