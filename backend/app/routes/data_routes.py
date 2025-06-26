from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.database import db
from app.models import DataType, DataPermission

data_bp = Blueprint('data', __name__)

@data_bp.route('/data-types', methods=['GET'])
@login_required
def get_data_types():
    """Get all available data types with user's permission status"""
    try:
        # Get all data types
        data_types = DataType.query.all()
        
        # Get user's current permissions
        user_permissions = DataPermission.query.filter_by(user_id=current_user.id).all()
        permission_dict = {perm.data_type_id: perm for perm in user_permissions}
        
        # Build response with permission status
        result = []
        for data_type in data_types:
            permission = permission_dict.get(data_type.id)
            
            data_type_info = data_type.to_dict()
            data_type_info.update({
                'enabled': permission.enabled if permission else False,
                'grantedAt': permission.granted_at.isoformat() if permission and permission.granted_at else None,
                'lastAccessed': permission.last_accessed.isoformat() if permission and permission.last_accessed else None,
                'lastRequest': 'Nie' if not permission or not permission.last_accessed else permission.last_accessed.strftime('%d.%m.%Y')
            })
            
            result.append(data_type_info)
        
        return jsonify({
            'success': True,
            'dataTypes': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/data-permissions', methods=['GET'])
@login_required
def get_data_permissions():
    """Get user's current data permissions"""
    try:
        permissions = DataPermission.query.filter_by(user_id=current_user.id).all()
        
        result = []
        for permission in permissions:
            perm_data = permission.to_dict()
            # Add data type info
            if permission.data_type:
                perm_data['dataType'] = permission.data_type.to_dict()
            result.append(perm_data)
        
        return jsonify({
            'success': True,
            'permissions': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/data-permissions', methods=['POST'])
@login_required
def update_data_permission():
    """Update or create a data permission for the user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        data_type_id = data.get('dataTypeId')
        enabled = data.get('enabled', False)
        
        if not data_type_id:
            return jsonify({'error': 'dataTypeId is required'}), 400
            
        # Validate data type exists
        data_type = DataType.query.get(data_type_id)
        if not data_type:
            return jsonify({'error': 'Data type not found'}), 404
            
        # Get or create permission
        permission = DataPermission.query.filter_by(
            user_id=current_user.id,
            data_type_id=data_type_id
        ).first()
        
        if not permission:
            # Create new permission
            permission = DataPermission(
                user_id=current_user.id,
                data_type_id=data_type_id,
                enabled=enabled,
                granted_at=datetime.utcnow() if enabled else None
            )
            db.session.add(permission)
        else:
            # Update existing permission
            permission.enabled = enabled
            if enabled and not permission.granted_at:
                permission.granted_at = datetime.utcnow()
        
        db.session.commit()
        
        # Create an activity entry for transparency
        from app.models import Activity
        activity = Activity(
            user_id=current_user.id,
            title=f"Datenfreigabe {'aktiviert' if enabled else 'deaktiviert'}",
            description=f"Du hast die Freigabe für '{data_type.name}' {'aktiviert' if enabled else 'deaktiviert'}.",
            activity_type='data_permission',
            earning=0.0,
            company='DataFair'
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"Datenfreigabe für '{data_type.name}' {'aktiviert' if enabled else 'deaktiviert'}",
            'permission': permission.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/data-permissions/<int:permission_id>', methods=['DELETE'])
@login_required
def delete_data_permission(permission_id):
    """Delete a data permission (revoke access completely)"""
    try:
        permission = DataPermission.query.filter_by(
            id=permission_id,
            user_id=current_user.id
        ).first()
        
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404
            
        data_type_name = permission.data_type.name if permission.data_type else 'Unknown'
        
        db.session.delete(permission)
        
        # Create activity entry
        from app.models import Activity
        activity = Activity(
            user_id=current_user.id,
            title="Datenfreigabe entfernt",
            description=f"Du hast die Freigabe für '{data_type_name}' vollständig entfernt.",
            activity_type='data_permission',
            earning=0.0,
            company='DataFair'
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"Datenfreigabe für '{data_type_name}' vollständig entfernt"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/data-usage', methods=['GET'])
@login_required
def get_data_usage():
    """Get data usage statistics for the user"""
    try:
        # Get user's enabled permissions
        enabled_permissions = DataPermission.query.filter_by(
            user_id=current_user.id,
            enabled=True
        ).all()
        
        # Calculate potential monthly earnings
        total_monthly_value = sum(
            perm.data_type.monthly_value for perm in enabled_permissions 
            if perm.data_type
        )
        
        # Get usage statistics (mock data for now)
        usage_stats = {
            'totalDataTypes': len(enabled_permissions),
            'monthlyValue': total_monthly_value,
            'lastAccess': max(
                (perm.last_accessed for perm in enabled_permissions if perm.last_accessed),
                default=None
            ),
            'totalRequests': sum(1 for perm in enabled_permissions if perm.last_accessed)  # Simple count
        }
        
        if usage_stats['lastAccess']:
            usage_stats['lastAccess'] = usage_stats['lastAccess'].isoformat()
        
        return jsonify({
            'success': True,
            'usage': usage_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500