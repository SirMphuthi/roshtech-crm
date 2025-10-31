from flask import Blueprint, jsonify, request, abort
from flask_login import current_user, login_required
from .models import Account, Contact, Opportunity
from . import db, limiter
from .models import Token, User
from flask import g
import secrets
from datetime import datetime, timedelta
from sqlalchemy import and_

def token_auth_required(f):
    """Decorator to require API token in Authorization header or ?token= param.
    Sets `g.current_api_user` when valid.
    """
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        token_value = None
        if auth and auth.lower().startswith('bearer '):
            token_value = auth.split(None, 1)[1].strip()
        if not token_value:
            token_value = request.args.get('token')

        if not token_value:
            abort(401)

        # Use prefix to narrow down candidates, then verify hash
        prefix = token_value[:8]
        candidates = Token.query.filter_by(token_prefix=prefix, revoked=False).all()
        token = None
        for t in candidates:
            if t.check_token(token_value):
                token = t
                break
        if not token:
            abort(401)
        # Check expiry
        if token.expires_at and datetime.utcnow() > token.expires_at:
            abort(401)

        g.current_api_user = token.user
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

api = Blueprint('api', __name__, url_prefix='/api')

def paginate_query(query):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    return items, pagination

@api.route('/accounts', methods=['GET'])
@limiter.limit("30/minute")
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


@api.route('/token', methods=['POST'])
@login_required
@limiter.limit("5/hour")
def create_token():
    """Create a new token for the currently logged-in user.
    This endpoint expects the user to be logged in via session (or run from the web UI).
    If you want purely API token creation, it's better to add an OAuth flow or admin-only token creation.
    """
    # We'll create a 48-byte URL-safe token
    value = secrets.token_urlsafe(48)
    token = Token(user_id=current_user.id)
    token.set_token(value)
    # optional: accept expires_in (seconds) and scopes from form/json
    expires_in = request.json.get('expires_in') if request.is_json else request.form.get('expires_in')
    if expires_in:
        try:
            token.expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
        except Exception:
            pass
    scopes = request.json.get('scopes') if request.is_json else request.form.get('scopes')
    if scopes:
        token.scopes = scopes
    db.session.add(token)
    db.session.commit()
    # return the plaintext token once to the caller
    return jsonify({'token': value, 'id': token.id})


@api.route('/token/<int:token_id>/revoke', methods=['POST'])
@login_required
def revoke_token(token_id):
    token = Token.query.get_or_404(token_id)
    if token.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
    token.revoke()
    return jsonify({'revoked': True})

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
