"""Routes for the CRM application."""
from datetime import datetime, timedelta
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from . import db
from .models import User, Account, Contact, Opportunity
from .models import Token

# A Blueprint is a way to organize a group of related routes.
main = Blueprint('main', __name__)

def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Explicitly require authentication first, then role check.
        if not current_user.is_authenticated:
            return redirect(url_for('main.login'))
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the login page and form submission."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Look up the user in the database by their email.
        user = User.query.filter_by(email=email).first()
        
        # Check if the user exists and if the password is correct.
        if user and user.check_password(password):
            # Log the user in (this creates their session).
            login_user(user)
            # Before redirecting, check if they were trying to access a protected page
            next_page = request.args.get('next')
            # Make sure the next page is safe (starts with /)
            if next_page and next_page.startswith('/'):
                # Check if they were trying to access an admin page without admin rights
                if '/users' in next_page and user.role != 'admin':
                    flash('Access denied: Admin privileges required.', 'error')
                    return redirect(url_for('main.dashboard'))
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            # If login fails, show an error message.
            flash('Invalid email or password. Please try again.', 'danger')

    # If it's a GET request, just show the login page.
    return render_template('login.html', title='Login')

@main.route('/logout')
@login_required
def logout():
    """Logs the user out."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/')
def index():
    """Redirect root URL to dashboard if logged in, or login page if not."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard showing key metrics and recent items."""
    # Get recent accounts and open opportunities
    accounts = Account.query.order_by(Account.created_at.desc()).limit(5).all()
    opportunities = Opportunity.query.filter(
        Opportunity.stage.notin_(['Closed-Won', 'Closed-Lost'])
    ).order_by(Opportunity.close_date.asc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         title='Dashboard',
                         accounts=accounts, 
                         opportunities=opportunities)

@main.route('/users')
@admin_required  # Only admins can see user list
def users():
    """List users with pagination and search (admin only)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '', type=str)

    base = User.query
    if q:
        pattern = f"%{q}%"
        base = base.filter(User.email.ilike(pattern) | User.first_name.ilike(pattern) | User.last_name.ilike(pattern))

    pagination = base.order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    return render_template('users/list.html', users=users, pagination=pagination, q=q, title='Users')

@main.route('/users/create', methods=['GET', 'POST'])
@admin_required
def user_create():
    """Create a new user."""
    if request.method == 'POST':
        email = request.form.get('email')
        if User.query.filter_by(email=email).first():
            # If AJAX/JSON request, return JSON error
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return {'success': False, 'error': 'Email already registered'}, 400
            flash('Email already registered', 'error')
            return render_template('users/form.html', title='Create User')
        
        user = User(
            email=email,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            role=request.form.get('role', 'user')
        )
        user.set_password(request.form.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        # If AJAX, return JSON payload describing the new user so frontend can update
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return {
                'success': True,
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }

        flash('User created successfully', 'success')
        return redirect(url_for('main.users'))
    
    return render_template('users/form.html', title='Create User')

@main.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):
    """Edit an existing user."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    
    if request.method == 'POST':
        email = request.form.get('email')
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user and existing_user.id != user_id:
            flash('Email already registered', 'error')
            return render_template('users/form.html', user=user, title='Edit User')
        
        user.email = email
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.role = request.form.get('role', 'user')
        
        db.session.commit()
        # If AJAX, return JSON so frontend can update inline
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return {
                'success': True,
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }

        flash('User updated successfully', 'success')
        return redirect(url_for('main.users'))
    
    return render_template('users/form.html', user=user, title='Edit User')

@main.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def user_delete(user_id):
    """Delete a user."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('main.users'))
    
    db.session.delete(user)
    db.session.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return {'success': True, 'id': user_id}

    flash('User deleted successfully', 'success')
    return redirect(url_for('main.users'))


@main.route('/users/<int:user_id>/json')
@admin_required
def user_json(user_id):
    """Return JSON details for a user (admin only)."""
    u = db.session.get(User, user_id)
    if not u:
        abort(404)
    return {
        'id': u.id,
        'email': u.email,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'role': u.role
    }

@main.route('/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def user_reset_password(user_id):
    """Reset a user's password."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    new_password = request.form.get('new_password')
    
    user.set_password(new_password)
    db.session.commit()
    
    flash('Password reset successfully', 'success')
    return redirect(url_for('main.user_edit', user_id=user_id))

@main.route('/tokens')
@admin_required
def tokens_list():
    """Admin list of tokens."""
    tokens = Token.query.order_by(Token.created_at.desc()).all()
    return render_template('users/tokens.html', tokens=tokens, title='API Tokens')

@main.route('/tokens/create', methods=['POST'])
@admin_required
def tokens_create():
    """Create a token for a user (admin action)"""
    user_id = request.form.get('user_id')
    expires_in = request.form.get('expires_in')
    scopes = request.form.get('scopes')
    
    if not user_id:
        flash('User is required', 'error')
        return redirect(url_for('main.tokens_list'))
        
    user = db.session.get(User, int(user_id))
    if not user:
        abort(404)
    value = secrets.token_urlsafe(48)
    token = Token(user_id=user.id)
    token.set_token(value)
    
    if expires_in:
        try:
            token.expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
        except Exception:
            pass
            
    token.scopes = scopes
    db.session.add(token)
    db.session.commit()
    # If this is an AJAX request, return JSON with the token value and metadata
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return {
            'success': True,
            'token': value,
            'id': token.id,
            'token_prefix': token.token_prefix,
            'created_at': token.created_at.isoformat(),
            'expires_at': token.expires_at.isoformat() if token.expires_at else None,
            'user_email': user.email,
            'scopes': token.scopes
        }

    flash(f'Token created: {value} (copy it now, it will not be shown again)', 'success')
    return redirect(url_for('main.tokens_list'))

@main.route('/tokens/<int:token_id>/revoke', methods=['POST'])
@admin_required
def tokens_revoke(token_id):
    """Revoke a token."""
    token = db.session.get(Token, token_id)
    if not token:
        abort(404)
    token.revoke()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return {'success': True, 'id': token_id}

    flash('Token revoked', 'success')
    return redirect(url_for('main.tokens_list'))

@main.route('/opportunities')
@login_required
def opportunities():
    """List opportunities with pagination, search and RBAC (sales see own deals)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '', type=str)

    base = Opportunity.query.join(Account)
    # Non-admin users only see their own opportunities
    if current_user.role != 'admin':
        base = base.filter(Opportunity.owner_id == current_user.id)

    if q:
        pattern = f"%{q}%"
        base = base.filter(Opportunity.name.ilike(pattern) | Account.name.ilike(pattern))

    pagination = base.order_by(Opportunity.close_date.asc()).paginate(page=page, per_page=per_page, error_out=False)
    opportunities = pagination.items
    return render_template('opportunities/list.html', opportunities=opportunities, pagination=pagination, q=q, title='Opportunities')

@main.route('/opportunities/create', methods=['GET', 'POST'])
@login_required
def opportunity_create():
    """Create a new opportunity."""
    if request.method == 'POST':
        account = db.session.get(Account, request.form.get('account_id'))
        if not account:
            flash('Invalid account selected', 'error')
            return redirect(url_for('main.opportunities'))
        
        opportunity = Opportunity(
            name=request.form.get('name'),
            stage=request.form.get('stage'),
            value=float(request.form.get('value', 0)),
            close_date=datetime.strptime(request.form.get('close_date'), '%Y-%m-%d'),
            account_id=account.id,
            owner_id=current_user.id
        )
        
        db.session.add(opportunity)
        db.session.commit()
        
        flash('Opportunity created successfully', 'success')
        return redirect(url_for('main.opportunities'))
    
    accounts = Account.query.all()
    return render_template('opportunities/form.html', accounts=accounts, title='Create Opportunity')

@main.route('/opportunities/<int:opportunity_id>/edit', methods=['GET', 'POST'])
@login_required
def opportunity_edit(opportunity_id):
    """Edit an existing opportunity."""
    opportunity = db.session.get(Opportunity, opportunity_id)
    if not opportunity:
        abort(404)
    
    # Only allow the owner or an admin to edit
    if opportunity.owner_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to edit this opportunity', 'error')
        return redirect(url_for('main.opportunities'))
    
    if request.method == 'POST':
        account = db.session.get(Account, request.form.get('account_id'))
        if not account:
            flash('Invalid account selected', 'error')
            return redirect(url_for('main.opportunities'))
        
        opportunity.name = request.form.get('name')
        opportunity.stage = request.form.get('stage')
        opportunity.value = float(request.form.get('value', 0))
        opportunity.close_date = datetime.strptime(request.form.get('close_date'), '%Y-%m-%d')
        opportunity.account_id = account.id
        
        db.session.commit()
        flash('Opportunity updated successfully', 'success')
        return redirect(url_for('main.opportunities'))
    
    accounts = Account.query.all()
    return render_template('opportunities/form.html', opportunity=opportunity, accounts=accounts, title='Edit Opportunity')

@main.route('/opportunities/<int:opportunity_id>/delete', methods=['POST'])
@login_required
def opportunity_delete(opportunity_id):
    """Delete an opportunity."""
    opportunity = db.session.get(Opportunity, opportunity_id)
    if not opportunity:
        abort(404)
    
    # Only allow the owner or an admin to delete
    if opportunity.owner_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to delete this opportunity', 'error')
        return redirect(url_for('main.opportunities'))
    
    db.session.delete(opportunity)
    db.session.commit()
    flash('Opportunity deleted successfully', 'success')
    return redirect(url_for('main.opportunities'))

@main.route('/contacts')
@login_required
def contacts():
    """List contacts with pagination and search."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '', type=str)

    base = Contact.query.join(Account)
    if q:
        pattern = f"%{q}%"
        base = base.filter(Contact.first_name.ilike(pattern) | Contact.last_name.ilike(pattern) | Contact.email.ilike(pattern) | Account.name.ilike(pattern))

    pagination = base.order_by(Contact.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    contacts = pagination.items
    return render_template('contacts/list.html', contacts=contacts, pagination=pagination, q=q, title='Contacts')

@main.route('/contacts/create', methods=['GET', 'POST'])
@login_required
def contact_create():
    """Create a new contact."""
    if request.method == 'POST':
        account = db.session.get(Account, request.form.get('account_id'))
        if not account:
            flash('Invalid account selected', 'error')
            return redirect(url_for('main.contacts'))
        
        contact = Contact(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            phone_number=request.form.get('phone_number'),
            role_title=request.form.get('role_title'),
            account_id=account.id
        )
        
        db.session.add(contact)
        db.session.commit()
        
        flash('Contact created successfully', 'success')
        return redirect(url_for('main.contacts'))
    
    accounts = Account.query.all()
    return render_template('contacts/form.html', accounts=accounts, title='Create Contact')

@main.route('/contacts/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
def contact_edit(contact_id):
    """Edit an existing contact."""
    contact = db.session.get(Contact, contact_id)
    if not contact:
        abort(404)
    
    if request.method == 'POST':
        account = db.session.get(Account, request.form.get('account_id'))
        if not account:
            flash('Invalid account selected', 'error')
            return redirect(url_for('main.contacts'))
        
        contact.first_name = request.form.get('first_name')
        contact.last_name = request.form.get('last_name')
        contact.email = request.form.get('email')
        contact.phone_number = request.form.get('phone_number')
        contact.role_title = request.form.get('role_title')
        contact.account_id = account.id
        
        db.session.commit()
        flash('Contact updated successfully', 'success')
        return redirect(url_for('main.contacts'))
    
    accounts = Account.query.all()
    return render_template('contacts/form.html', contact=contact, accounts=accounts, title='Edit Contact')

@main.route('/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def contact_delete(contact_id):
    """Delete a contact."""
    contact = db.session.get(Contact, contact_id)
    if not contact:
        abort(404)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully', 'success')
    return redirect(url_for('main.contacts'))