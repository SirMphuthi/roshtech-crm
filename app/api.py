from flask import Blueprint, jsonify, request, abort, make_response
from flask_login import current_user, login_required, login_user, logout_user
from flask import Response
from .models import Account, Contact, Opportunity, User, Token
from . import db
from flask import g
import secrets
from datetime import datetime, timedelta
from sqlalchemy import and_, func

api = Blueprint('api', __name__, url_prefix='/api')

# ===========================
# AUTH ENDPOINTS
# ===========================

@api.route('/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """Login with email and password. Returns user data and sets session."""
    if request.method == 'OPTIONS':
        # CORS preflight request
        return jsonify({'message': 'CORS preflight'}), 200
    # Debug logging for troubleshooting
    print('Headers:', dict(request.headers))
    print('Raw data:', request.data)
    try:
        json_data = request.get_json(force=True)
    except Exception as e:
        print('JSON parse error:', e)
        json_data = None
    print('JSON:', json_data)
    # Forced debug response to confirm code path
    return jsonify({'debug': 'Login endpoint reached', 'headers': dict(request.headers), 'raw_data': request.data.decode('utf-8'), 'json': json_data}), 200
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    login_user(user, remember=True)
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role
    })

# Global error handlers for JSON responses
@api.app_errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@api.app_errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Return JSON 401 for API endpoints if not authenticated
@api.app_errorhandler(401)
def unauthorized_error(error):
    return jsonify({'error': 'Unauthorized'}), 401

# Patch login_required to return JSON for API endpoints
def api_login_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)
    return decorated_view

# Replace all @login_required with @api_login_required in this file

@api.route('/auth/logout', methods=['POST'])
@api_login_required
def logout():
    """Logout the current user."""
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@api.route('/auth/me', methods=['GET'])
@api_login_required
def get_current_user():
    """Get current logged-in user info."""
    user = current_user
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role
    }), 200

# ===========================
# DASHBOARD STATS
# ===========================


@api.route('/dashboard/stats', methods=['GET'])
@api_login_required
def dashboard_stats():
    """Get dashboard statistics."""
    accounts_count = Account.query.count()
    contacts_count = Contact.query.count()
    opportunities_count = Opportunity.query.count()
    total_opportunity_value = db.session.query(func.sum(Opportunity.value)).scalar() or 0
    
    return jsonify({
        'accounts': accounts_count,
        'contacts': contacts_count,
        'opportunities': opportunities_count,
        'total_opportunity_value': total_opportunity_value
    }), 200

# ===========================
# ACCOUNTS ENDPOINTS
# ===========================

@api.route('/accounts', methods=['GET'])
@api_login_required
def list_accounts():
    """List all accounts with pagination and search."""
    q = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Account.query
    if q:
        pattern = f"%{q}%"
        query = query.filter(Account.name.ilike(pattern))
    
    pagination = query.order_by(Account.name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    data = [{
        'id': a.id,
        'name': a.name,
        'industry': a.industry,
        'phone': a.phone,
        'website': a.website,
        'owner_id': a.owner_id
    } for a in items]
    
    return jsonify({
        'items': data,
        'page': pagination.page,
        'total': pagination.total,
        'pages': pagination.pages
    }), 200

@api.route('/accounts', methods=['POST'])
@api_login_required
def create_account():
    """Create a new account."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Account name required'}), 400
    
    if Account.query.filter_by(name=name).first():
        return jsonify({'error': 'Account already exists'}), 409
    
    account = Account(
        name=name,
        industry=data.get('industry', ''),
        phone=data.get('phone', ''),
        website=data.get('website', ''),
        owner_id=current_user.id
    )
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'id': account.id,
        'name': account.name,
        'industry': account.industry,
        'phone': account.phone,
        'website': account.website
    }), 201

@api.route('/accounts/<int:account_id>', methods=['GET'])
@api_login_required
def get_account(account_id):
    """Get a single account."""
    account = Account.query.get_or_404(account_id)
    return jsonify({
        'id': account.id,
        'name': account.name,
        'industry': account.industry,
        'phone': account.phone,
        'website': account.website,
        'owner_id': account.owner_id,
        'created_at': account.created_at.isoformat() if account.created_at else None
    }), 200

@api.route('/accounts/<int:account_id>', methods=['PUT'])
@api_login_required
def update_account(account_id):
    """Update an account."""
    account = Account.query.get_or_404(account_id)
    if account.owner_id != current_user.id and current_user.role not in ['admin', 'owner']:
        abort(403)
    
    data = request.get_json() or {}
    if 'name' in data:
        account.name = data['name'].strip()
    if 'industry' in data:
        account.industry = data['industry']
    if 'phone' in data:
        account.phone = data['phone']
    if 'website' in data:
        account.website = data['website']
    
    db.session.commit()
    return jsonify({'message': 'Account updated'}), 200

@api.route('/accounts/<int:account_id>', methods=['DELETE'])
@api_login_required
def delete_account(account_id):
    """Delete an account."""
    account = Account.query.get_or_404(account_id)
    if account.owner_id != current_user.id and current_user.role not in ['admin', 'owner']:
        abort(403)
    
    db.session.delete(account)
    db.session.commit()
    return jsonify({'message': 'Account deleted'}), 200

# ===========================
# CONTACTS ENDPOINTS
# ===========================

@api.route('/contacts', methods=['GET'])
@api_login_required
def list_contacts():
    """List all contacts with pagination and search."""
    q = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Contact.query.join(Account)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            Contact.first_name.ilike(pattern) |
            Contact.last_name.ilike(pattern) |
            Contact.email.ilike(pattern) |
            Account.name.ilike(pattern)
        )
    
    pagination = query.order_by(Contact.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    data = [{
        'id': c.id,
        'first_name': c.first_name,
        'last_name': c.last_name,
        'email': c.email,
        'phone_number': c.phone_number,
        'role_title': c.role_title,
        'account_id': c.account_id,
        'account_name': c.account.name
    } for c in items]
    
    return jsonify({
        'items': data,
        'page': pagination.page,
        'total': pagination.total,
        'pages': pagination.pages
    }), 200

@api.route('/contacts', methods=['POST'])
@api_login_required
def create_contact():
    """Create a new contact."""
    data = request.get_json() or {}
    first_name = data.get('first_name', '').strip()
    account_id = data.get('account_id')
    
    if not first_name or not account_id:
        return jsonify({'error': 'first_name and account_id required'}), 400
    
    if not Account.query.get(account_id):
        return jsonify({'error': 'Account not found'}), 404
    
    contact = Contact(
        first_name=first_name,
        last_name=data.get('last_name', ''),
        email=data.get('email', ''),
        phone_number=data.get('phone_number', ''),
        role_title=data.get('role_title', ''),
        account_id=account_id
    )
    db.session.add(contact)
    db.session.commit()
    
    return jsonify({
        'id': contact.id,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'email': contact.email,
        'phone_number': contact.phone_number,
        'account_id': contact.account_id
    }), 201

@api.route('/contacts/<int:contact_id>', methods=['GET'])
@api_login_required
def get_contact(contact_id):
    """Get a single contact."""
    contact = Contact.query.get_or_404(contact_id)
    return jsonify({
        'id': contact.id,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'email': contact.email,
        'phone_number': contact.phone_number,
        'role_title': contact.role_title,
        'account_id': contact.account_id
    }), 200

@api.route('/contacts/<int:contact_id>', methods=['PUT'])
@api_login_required
def update_contact(contact_id):
    """Update a contact."""
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json() or {}
    
    if 'first_name' in data:
        contact.first_name = data['first_name'].strip()
    if 'last_name' in data:
        contact.last_name = data['last_name']
    if 'email' in data:
        contact.email = data['email']
    if 'phone_number' in data:
        contact.phone_number = data['phone_number']
    if 'role_title' in data:
        contact.role_title = data['role_title']
    
    db.session.commit()
    return jsonify({'message': 'Contact updated'}), 200

@api.route('/contacts/<int:contact_id>', methods=['DELETE'])
@api_login_required
def delete_contact(contact_id):
    """Delete a contact."""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': 'Contact deleted'}), 200

# ===========================
# OPPORTUNITIES ENDPOINTS
# ===========================

@api.route('/opportunities', methods=['GET'])
@api_login_required
def list_opportunities():
    """List all opportunities with pagination and search."""
    q = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Opportunity.query.join(Account)
    
    # RBAC: non-admins see only their opportunities
    if current_user.role not in ['admin', 'owner']:
        query = query.filter(Opportunity.owner_id == current_user.id)
    
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            Opportunity.name.ilike(pattern) |
            Account.name.ilike(pattern)
        )
    
    pagination = query.order_by(Opportunity.close_date.asc()).paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    data = [{
        'id': o.id,
        'name': o.name,
        'stage': o.stage,
        'value': o.value,
        'close_date': o.close_date.isoformat() if o.close_date else None,
        'account_id': o.account_id,
        'account_name': o.account.name,
        'owner_id': o.owner_id,
        'created_at': o.created_at.isoformat() if o.created_at else None
    } for o in items]
    
    return jsonify({
        'items': data,
        'page': pagination.page,
        'total': pagination.total,
        'pages': pagination.pages
    }), 200

@api.route('/opportunities', methods=['POST'])
@api_login_required
def create_opportunity():
    """Create a new opportunity."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    account_id = data.get('account_id')
    
    if not name or not account_id:
        return jsonify({'error': 'name and account_id required'}), 400
    
    if not Account.query.get(account_id):
        return jsonify({'error': 'Account not found'}), 404
    
    opportunity = Opportunity(
        name=name,
        stage=data.get('stage', 'Prospecting'),
        value=data.get('value', 0),
        account_id=account_id,
        owner_id=current_user.id
    )
    db.session.add(opportunity)
    db.session.commit()
    
    return jsonify({
        'id': opportunity.id,
        'name': opportunity.name,
        'stage': opportunity.stage,
        'value': opportunity.value,
        'account_id': opportunity.account_id
    }), 201

@api.route('/opportunities/<int:opportunity_id>', methods=['GET'])
@api_login_required
def get_opportunity(opportunity_id):
    """Get a single opportunity."""
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    
    # RBAC check
    if current_user.role not in ['admin', 'owner'] and opportunity.owner_id != current_user.id:
        abort(403)
    
    return jsonify({
        'id': opportunity.id,
        'name': opportunity.name,
        'stage': opportunity.stage,
        'value': opportunity.value,
        'close_date': opportunity.close_date.isoformat() if opportunity.close_date else None,
        'account_id': opportunity.account_id,
        'owner_id': opportunity.owner_id,
        'created_at': opportunity.created_at.isoformat() if opportunity.created_at else None
    }), 200

@api.route('/opportunities/<int:opportunity_id>', methods=['PUT'])
@api_login_required
def update_opportunity(opportunity_id):
    """Update an opportunity."""
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    
    # RBAC check
    if current_user.role not in ['admin', 'owner'] and opportunity.owner_id != current_user.id:
        abort(403)
    
    data = request.get_json() or {}
    
    if 'name' in data:
        opportunity.name = data['name'].strip()
    if 'stage' in data:
        opportunity.stage = data['stage']
    if 'value' in data:
        opportunity.value = data['value']
    if 'close_date' in data:
        opportunity.close_date = data['close_date']
    
    db.session.commit()
    return jsonify({'message': 'Opportunity updated'}), 200

@api.route('/opportunities/<int:opportunity_id>', methods=['DELETE'])
@api_login_required
def delete_opportunity(opportunity_id):
    """Delete an opportunity."""
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    
    # RBAC check
    if current_user.role not in ['admin', 'owner'] and opportunity.owner_id != current_user.id:
        abort(403)
    
    db.session.delete(opportunity)
    db.session.commit()
    return jsonify({'message': 'Opportunity deleted'}), 200

# ===========================
# LEADS ENDPOINTS
# ===========================

@api.route('/leads', methods=['GET'])
@api_login_required
def list_leads():
    """List all leads (using Opportunities model as Leads)."""
    return list_opportunities()

@api.route('/leads', methods=['POST'])
@api_login_required
def create_lead():
    """Create a new lead."""
    return create_opportunity()

@api.route('/leads/<int:lead_id>', methods=['GET'])
@api_login_required
def get_lead(lead_id):
    """Get a single lead."""
    return get_opportunity(lead_id)

@api.route('/leads/<int:lead_id>', methods=['PUT'])
@api_login_required
def update_lead(lead_id):
    """Update a lead."""
    return update_opportunity(lead_id)

@api.route('/leads/<int:lead_id>', methods=['DELETE'])
@api_login_required
def delete_lead(lead_id):
    """Delete a lead."""
    return delete_opportunity(lead_id)

# ===========================
# TASKS ENDPOINTS (placeholder)
# ===========================

@api.route('/tasks', methods=['GET'])
@api_login_required
def list_tasks():
    """List all tasks."""
    return jsonify({
        'items': [],
        'page': 1,
        'total': 0,
        'pages': 1,
        'message': 'Tasks module not yet implemented'
    }), 200

@api.route('/tasks', methods=['POST'])
@api_login_required
def create_task():
    """Create a new task."""
    return jsonify({'error': 'Tasks module not yet implemented'}), 501

# ===========================
# REPORTS ENDPOINTS (placeholder)
# ===========================

@api.route('/reports', methods=['GET'])
@api_login_required
def list_reports():
    """List available reports."""
    return jsonify({
        'items': [],
        'message': 'Reports module not yet implemented'
    }), 200

# ===========================
# ERROR HANDLERS
# ===========================

@api.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@api.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Unauthorized'}), 401

@api.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Forbidden'}), 403
