from flask import Blueprint, jsonify, request, abort
from flask_login import current_user
from .models import Account, Contact, Opportunity
from . import db

api = Blueprint('api', __name__, url_prefix='/api')

def paginate_query(query):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    return items, pagination

@api.route('/accounts', methods=['GET'])
def list_accounts():
    q = request.args.get('q', '', type=str)
    base = Account.query
    if q:
        pattern = f"%{q}%"
        base = base.filter(Account.name.ilike(pattern))
    items, pagination = paginate_query(base.order_by(Account.name.asc()))
    data = [{
        'id': a.id,
        'name': a.name,
        'industry': a.industry,
        'phone': a.phone,
        'website': a.website
    } for a in items]
    return jsonify({'items': data, 'page': pagination.page, 'total': pagination.total})

@api.route('/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
    a = Account.query.get_or_404(account_id)
    return jsonify({'id': a.id, 'name': a.name, 'industry': a.industry, 'phone': a.phone, 'website': a.website})

@api.route('/contacts', methods=['GET'])
def list_contacts():
    q = request.args.get('q', '', type=str)
    base = Contact.query.join(Account)
    if q:
        pattern = f"%{q}%"
        base = base.filter(Contact.first_name.ilike(pattern) | Contact.last_name.ilike(pattern) | Contact.email.ilike(pattern) | Account.name.ilike(pattern))
    items, pagination = paginate_query(base.order_by(Contact.id.desc()))
    data = [{
        'id': c.id,
        'first_name': c.first_name,
        'last_name': c.last_name,
        'email': c.email,
        'phone_number': c.phone_number,
        'account_id': c.account_id,
        'account_name': c.account.name
    } for c in items]
    return jsonify({'items': data, 'page': pagination.page, 'total': pagination.total})

@api.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    c = Contact.query.get_or_404(contact_id)
    return jsonify({'id': c.id, 'first_name': c.first_name, 'last_name': c.last_name, 'email': c.email, 'phone_number': c.phone_number, 'account_id': c.account_id})

@api.route('/opportunities', methods=['GET'])
def list_opportunities():
    q = request.args.get('q', '', type=str)
    base = Opportunity.query.join(Account)
    # apply RBAC: non-admins see only their opportunities
    if not current_user.is_anonymous and getattr(current_user, 'role', None) != 'admin':
        base = base.filter(Opportunity.owner_id == current_user.id)
    if q:
        pattern = f"%{q}%"
        base = base.filter(Opportunity.name.ilike(pattern) | Account.name.ilike(pattern))
    items, pagination = paginate_query(base.order_by(Opportunity.close_date.asc()))
    data = [{
        'id': o.id,
        'name': o.name,
        'stage': o.stage,
        'value': o.value,
        'close_date': o.close_date.isoformat() if o.close_date else None,
        'account_id': o.account_id,
        'account_name': o.account.name,
        'owner_id': o.owner_id
    } for o in items]
    return jsonify({'items': data, 'page': pagination.page, 'total': pagination.total})

@api.route('/opportunities/<int:opportunity_id>', methods=['GET'])
def get_opportunity(opportunity_id):
    o = Opportunity.query.get_or_404(opportunity_id)
    # check RBAC
    if not current_user.is_anonymous and getattr(current_user, 'role', None) != 'admin' and o.owner_id != current_user.id:
        abort(403)
    return jsonify({'id': o.id, 'name': o.name, 'stage': o.stage, 'value': o.value, 'close_date': o.close_date.isoformat() if o.close_date else None, 'account_id': o.account_id, 'owner_id': o.owner_id})
