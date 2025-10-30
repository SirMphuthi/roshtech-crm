from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from . import db
from .models import User, Account, Contact, Opportunity

# A Blueprint is a way to organize a group of related routes.
# We call it 'main' here.
main = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to require one of the provided roles on a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
        account = Account.query.get(request.form.get('account_id'))
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
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    
    if request.method == 'POST':
        account = Account.query.get(request.form.get('account_id'))
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
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    
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
        account = Account.query.get(request.form.get('account_id'))
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
    contact = Contact.query.get_or_404(contact_id)
    
    if request.method == 'POST':
        account = Account.query.get(request.form.get('account_id'))
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
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully', 'success')
    return redirect(url_for('main.contacts'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the login page and form submission."""
    
    # If the user is already logged in, send them to the dashboard.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Look up the user in the database by their email.
        user = User.query.filter_by(email=email).first()
        
        # Check if the user exists and if the password is correct.
        if user and user.check_password(password):
            # Log the user in (this creates their session).
            login_user(user)
            # Send them to the dashboard.
            return redirect(url_for('main.index'))
        else:
            # If login fails, show an error message.
            flash('Invalid email or password. Please try again.', 'danger')

    # If it's a GET request, just show the login page.
    return render_template('login.html', title='Login')

@main.route('/logout')
@login_required  # This route can only be accessed by a logged-in user.
def logout():
    """Logs the user out."""
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/')
@main.route('/dashboard')
@login_required  # This route is protected.
def index():
    """Displays the main CRM dashboard."""
    
    # --- Example Data for the Dashboard ---
    # In the future, we will fetch this data based on the current_user.
    # For now, we fetch all accounts and opportunities to show.
    
    accounts = Account.query.order_by(Account.created_at.desc()).limit(5).all()
    opportunities = Opportunity.query.filter(Opportunity.stage.notin_(['Closed-Won', 'Closed-Lost'])).order_by(Opportunity.close_date.asc()).limit(5).all()

    return render_template('dashboard.html', 
                           title='Dashboard', 
                           accounts=accounts, 
                           opportunities=opportunities)

@main.route('/users')
@login_required
@admin_required
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
    return render_template('users/list.html', users=users, pagination=pagination, q=q, title='User Management')

@main.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def user_create():
    """Create a new user."""
    if request.method == 'POST':
        email = request.form.get('email')
        if User.query.filter_by(email=email).first():
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
        
        flash('User created successfully', 'success')
        return redirect(url_for('main.users'))
    
    return render_template('users/form.html', title='Create User')

@main.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    """Edit an existing user."""
    user = User.query.get_or_404(user_id)
    
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
        flash('User updated successfully', 'success')
        return redirect(url_for('main.users'))
    
    return render_template('users/form.html', user=user, title='Edit User')

@main.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('main.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('main.users'))

@main.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def user_reset_password(user_id):
    """Reset a user's password."""
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    user.set_password(new_password)
    db.session.commit()
    
    flash('Password reset successfully', 'success')
    return redirect(url_for('main.user_edit', user_id=user_id))
