"""Routes for the CRM application."""
from datetime import datetime, timedelta
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from . import db
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import smtplib
from email.message import EmailMessage
import json
from pathlib import Path
import io
import csv
from flask import Response
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
        # Allow both 'admin' and 'owner' roles full access
        if current_user.role not in ('admin', 'owner'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def _get_serializer():
    secret = current_app.config.get('SECRET_KEY')
    return URLSafeTimedSerializer(secret)


def _audit_event(action: str, actor_id: int | None, details: dict):
    """Append an audit event JSON line to instance/audit.log"""
    try:
        inst = Path(current_app.instance_path)
        inst.mkdir(parents=True, exist_ok=True)
        log_file = inst / 'audit.log'
        event = {
            'action': action,
            'actor_id': actor_id,
            'details': details,
            'ts': datetime.utcnow().isoformat()
        }
        with log_file.open('a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        current_app.logger.exception('Failed to write audit event')


@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            s = _get_serializer()
            token = s.dumps({'user_id': user.id})
            reset_url = url_for('main.reset_password', token=token, _external=True)
            # Try to send an email if mail settings are configured; otherwise log the link
            mail_server = current_app.config.get('MAIL_SERVER')
            if mail_server:
                try:
                    msg = EmailMessage()
                    msg['Subject'] = 'RoshTech CRM - Password reset'
                    msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER')
                    msg['To'] = user.email
                    msg.set_content(f'Use the following link to reset your password (valid 1 hour):\n\n{reset_url}')

                    host = current_app.config.get('MAIL_SERVER')
                    port = current_app.config.get('MAIL_PORT') or 25
                    use_tls = current_app.config.get('MAIL_USE_TLS')
                    username = current_app.config.get('MAIL_USERNAME')
                    password = current_app.config.get('MAIL_PASSWORD')

                    server = smtplib.SMTP(host, port, timeout=10)
                    try:
                        if use_tls:
                            server.starttls()
                        if username and password:
                            server.login(username, password)
                        server.send_message(msg)
                        current_app.logger.info(f'Password reset email sent to {user.email}')
                    finally:
                        server.quit()
                    flash('If the email exists we sent a reset link to your inbox.', 'info')
                except Exception:
                    current_app.logger.exception('Failed to send password reset email, falling back to log')
                    current_app.logger.info(f'Password reset link for {email}: {reset_url}')
                    flash('Password reset link generated (check server logs).', 'info')
            else:
                current_app.logger.info(f'Password reset link for {email}: {reset_url}')
                flash('If the email exists we sent a reset link (check server logs).', 'info')
        else:
            flash('If the email exists we sent a reset link (check server logs).', 'info')
        return redirect(url_for('main.login'))

    return render_template('forgot_password.html', title='Forgot Password')


@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        s = _get_serializer()
        data = s.loads(token, max_age=3600)
    except SignatureExpired:
        flash('The password reset link has expired.', 'error')
        return redirect(url_for('main.forgot_password'))
    except BadSignature:
        flash('Invalid password reset token.', 'error')
        return redirect(url_for('main.forgot_password'))

    user = db.session.get(User, data.get('user_id'))
    if not user:
        flash('Invalid user for password reset.', 'error')
        return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        if not new_password:
            flash('Password is required.', 'error')
            return render_template('reset_password.html', token=token)
        user.set_password(new_password)
        db.session.commit()
        flash('Your password has been reset. You may now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('reset_password.html', token=token, title='Reset Password')

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
    # Additional metrics
    total_accounts = Account.query.count()
    total_contacts = Contact.query.count()
    total_opps = Opportunity.query.count()
    # Read recent audit events (if available)
    recent_audit = []
    try:
        inst = Path(current_app.instance_path)
        log_file = inst / 'audit.log'
        if log_file.exists():
            with log_file.open(encoding='utf-8') as f:
                lines = f.readlines()[-20:]
                for ln in reversed(lines):
                    try:
                        recent_audit.append(json.loads(ln))
                    except Exception:
                        continue
    except Exception:
        current_app.logger.exception('Failed to read audit log')

    # Prepare simple chart data: opportunities by stage
    stages = {}
    for o in Opportunity.query.with_entities(Opportunity.stage).all():
        stages[o.stage] = stages.get(o.stage, 0) + 1

    return render_template('dashboard.html', 
                         title='Dashboard',
                         accounts=accounts, 
                         opportunities=opportunities,
                         total_accounts=total_accounts,
                         total_contacts=total_contacts,
                         total_opps=total_opps,
                         recent_audit=recent_audit,
                         opp_stage_data=stages)

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
        # audit
        _audit_event('user.create', current_user.id if current_user.is_authenticated else None, {'user_id': user.id, 'email': user.email})

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
        _audit_event('user.update', current_user.id if current_user.is_authenticated else None, {'user_id': user.id, 'email': user.email, 'role': user.role})

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
    _audit_event('user.delete', current_user.id if current_user.is_authenticated else None, {'user_id': user.id, 'email': user.email})
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


@main.route('/users/<int:user_id>/role', methods=['POST'])
@admin_required
def user_set_role(user_id):
    """Change a user's role (admin action)."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    new_role = request.form.get('role')
    if new_role not in ('user', 'admin', 'owner'):
        return ("Invalid role", 400)

    # For sensitive role changes require confirmation of current user's password
    confirm = request.form.get('confirm_password')
    if not confirm or not current_user.check_password(confirm):
        return ("Invalid confirmation password", 403)

    user.role = new_role
    db.session.commit()
    _audit_event('user.role_change', current_user.id if current_user.is_authenticated else None, {'user_id': user.id, 'new_role': new_role})

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return {'success': True, 'id': user.id, 'new_role': new_role}

    flash('User role updated', 'success')
    return redirect(url_for('main.users'))


@main.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """Owner/admin settings page (site name, SMTP settings)."""
    inst = Path(current_app.instance_path)
    inst.mkdir(parents=True, exist_ok=True)
    cfg_file = inst / 'settings.json'
    data = {}
    if cfg_file.exists():
        try:
            data = json.loads(cfg_file.read_text())
        except Exception:
            data = {}

    if request.method == 'POST':
        # Save settings
        data['site_name'] = request.form.get('site_name')
        data['mail_server'] = request.form.get('mail_server') or None
        data['mail_port'] = int(request.form.get('mail_port')) if request.form.get('mail_port') else None
        data['mail_username'] = request.form.get('mail_username') or None
        data['mail_password'] = request.form.get('mail_password') or None
        data['mail_use_tls'] = bool(request.form.get('mail_use_tls'))
        data['mail_default_sender'] = request.form.get('mail_default_sender') or None
        try:
            cfg_file.write_text(json.dumps(data, indent=2))
            flash('Settings saved', 'success')
            _audit_event('settings.update', current_user.id if current_user.is_authenticated else None, {'settings': ['site_name','mail_server','mail_port','mail_username','mail_use_tls','mail_default_sender']})
        except Exception:
            current_app.logger.exception('Failed to save settings')
            flash('Failed to save settings', 'error')
        # Also update current_app.config so changes take effect without restart
        current_app.config['MAIL_SERVER'] = data.get('mail_server')
        current_app.config['MAIL_PORT'] = data.get('mail_port')
        current_app.config['MAIL_USERNAME'] = data.get('mail_username')
        current_app.config['MAIL_PASSWORD'] = data.get('mail_password')
        current_app.config['MAIL_USE_TLS'] = data.get('mail_use_tls')
        current_app.config['MAIL_DEFAULT_SENDER'] = data.get('mail_default_sender')
        return redirect(url_for('main.settings'))

    return render_template('settings.html', settings=data, title='Settings')


@main.route('/settings/test-email', methods=['POST'])
@admin_required
def test_email():
    """Send a simple test email using current mail config or log the test link."""
    recipient = current_app.config.get('MAIL_DEFAULT_SENDER') or None
    if not recipient:
        return ("No default sender configured", 400)
    mail_server = current_app.config.get('MAIL_SERVER')
    s = 'This is a test email from RoshTech CRM.'
    if mail_server:
        try:
            msg = EmailMessage()
            msg['Subject'] = 'RoshTech CRM - Test Email'
            msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER')
            msg['To'] = recipient
            msg.set_content(s)
            server = smtplib.SMTP(current_app.config.get('MAIL_SERVER'), current_app.config.get('MAIL_PORT') or 25, timeout=10)
            try:
                if current_app.config.get('MAIL_USE_TLS'):
                    server.starttls()
                if current_app.config.get('MAIL_USERNAME') and current_app.config.get('MAIL_PASSWORD'):
                    server.login(current_app.config.get('MAIL_USERNAME'), current_app.config.get('MAIL_PASSWORD'))
                server.send_message(msg)
            finally:
                server.quit()
            _audit_event('settings.test_email', current_user.id if current_user.is_authenticated else None, {'to': recipient})
            return ('OK', 200)
        except Exception:
            current_app.logger.exception('Test email failed')
            return ('Failed to send test email (see logs)', 500)
    else:
        current_app.logger.info('Test email (no SMTP configured): %s', s)
        _audit_event('settings.test_email_logged', current_user.id if current_user.is_authenticated else None, {'note': 'logged only'})
        return ('Logged', 200)

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


@main.route('/opportunities/export')
@login_required
def opportunities_export():
    # Export visible opportunities as CSV
    base = Opportunity.query.join(Account)
    if current_user.role != 'admin':
        base = base.filter(Opportunity.owner_id == current_user.id)
    opportunities = base.order_by(Opportunity.close_date.asc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id','name','account','stage','value','close_date','owner'])
    for o in opportunities:
        writer.writerow([o.id, o.name, o.account.name if o.account else '', o.stage, o.value or 0, o.close_date.isoformat() if o.close_date else '', f"{o.owner.first_name} {o.owner.last_name}" if o.owner else ''])
    _audit_event('export.opportunities', current_user.id if current_user.is_authenticated else None, {'count': len(opportunities)})
    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=opportunities.csv"})

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


@main.route('/contacts/export')
@login_required
def contacts_export():
    base = Contact.query.join(Account)
    if current_user.role != 'admin':
        # non-admins see contacts via accounts they own? For now return all but this can be restricted
        base = base
    contacts = base.order_by(Contact.id.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id','first_name','last_name','email','phone','company'])
    for c in contacts:
        writer.writerow([c.id, c.first_name, c.last_name, c.email or '', c.phone_number or '', c.account.name if c.account else ''])
    _audit_event('export.contacts', current_user.id if current_user.is_authenticated else None, {'count': len(contacts)})
    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=contacts.csv"})


@main.route('/accounts')
@login_required
def accounts():
    """List accounts with pagination and search."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '', type=str)

    base = Account.query
    if q:
        pattern = f"%{q}%"
        base = base.filter(Account.name.ilike(pattern) | Account.industry.ilike(pattern))

    pagination = base.order_by(Account.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    accounts = pagination.items
    return render_template('accounts/list.html', accounts=accounts, pagination=pagination, q=q, title='Accounts')


@main.route('/accounts/export')
@login_required
def accounts_export():
    base = Account.query
    if current_user.role != 'admin':
        # For now all users can export; customize later to restrict
        base = base
    accounts = base.order_by(Account.name.asc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id','name','industry','phone','website','owner'])
    for a in accounts:
        writer.writerow([a.id, a.name, a.industry or '', a.phone or '', a.website or '', f"{a.owner.first_name} {a.owner.last_name}" if a.owner else ''])
    _audit_event('export.accounts', current_user.id if current_user.is_authenticated else None, {'count': len(accounts)})
    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=accounts.csv"})


@main.route('/accounts/import', methods=['POST'])
@login_required
def accounts_import():
    """Import accounts from an uploaded CSV file. Expected columns: name, industry, phone, website, owner_email(optional)"""
    f = request.files.get('file')
    if not f:
        flash('No file uploaded', 'error')
        return redirect(url_for('main.accounts'))

    try:
        data = f.read().decode('utf-8')
    except Exception:
        flash('Failed to read uploaded file (ensure UTF-8 CSV)', 'error')
        return redirect(url_for('main.accounts'))

    reader = csv.DictReader(io.StringIO(data))
    created = 0
    errors = []
    for idx, row in enumerate(reader, start=1):
        name = (row.get('name') or row.get('Name') or '').strip()
        if not name:
            errors.append(f'Row {idx}: missing name')
            continue
        if Account.query.filter_by(name=name).first():
            errors.append(f'Row {idx}: account "{name}" already exists')
            continue
        owner = None
        owner_email = (row.get('owner_email') or row.get('owner') or '').strip()
        if owner_email:
            owner = User.query.filter_by(email=owner_email).first()

        account = Account(
            name=name,
            industry=row.get('industry') or row.get('Industry'),
            phone=row.get('phone'),
            website=row.get('website'),
            owner_id=owner.id if owner else None
        )
        db.session.add(account)
        try:
            db.session.commit()
            created += 1
        except Exception as e:
            db.session.rollback()
            errors.append(f'Row {idx}: DB error: {e}')

    _audit_event('import.accounts', current_user.id if current_user.is_authenticated else None, {'created': created, 'errors': len(errors)})
    # Render a results page showing created count and any row errors
    return render_template('accounts/import_result.html', created=created, errors=errors, title='Import Results')


@main.route('/contacts/import', methods=['POST'])
@login_required
def contacts_import():
    """Import contacts from CSV. Expected headers: first_name,last_name,email,phone,role_title,company (account name)"""
    f = request.files.get('file')
    if not f:
        flash('No file uploaded', 'error')
        return redirect(url_for('main.contacts'))
    try:
        data = f.read().decode('utf-8')
    except Exception:
        flash('Failed to read uploaded file (ensure UTF-8 CSV)', 'error')
        return redirect(url_for('main.contacts'))

    reader = csv.DictReader(io.StringIO(data))
    created = 0
    errors = []
    for idx, row in enumerate(reader, start=1):
        first = (row.get('first_name') or row.get('First') or '').strip()
        last = (row.get('last_name') or row.get('Last') or '').strip()
        email = (row.get('email') or row.get('Email') or '').strip()
        company = (row.get('company') or row.get('Company') or row.get('account') or '').strip()
        if not first or not company:
            errors.append(f'Row {idx}: missing first_name or company')
            continue
        account = Account.query.filter_by(name=company).first()
        if not account:
            errors.append(f'Row {idx}: account "{company}" not found')
            continue
        contact = Contact(
            first_name=first,
            last_name=last,
            email=email,
            phone_number=row.get('phone'),
            role_title=row.get('role_title') or row.get('Role') or '',
            account_id=account.id
        )
        db.session.add(contact)
        try:
            db.session.commit()
            created += 1
        except Exception as e:
            db.session.rollback()
            errors.append(f'Row {idx}: DB error: {e}')

    _audit_event('import.contacts', current_user.id if current_user.is_authenticated else None, {'created': created, 'errors': len(errors)})
    return render_template('accounts/import_result.html', created=created, errors=errors, title='Contacts Import Results')


@main.route('/opportunities/import', methods=['POST'])
@login_required
def opportunities_import():
    """Import opportunities from CSV. Expected headers: name,account,stage,value,close_date(YYYY-MM-DD),owner_email(optional)"""
    f = request.files.get('file')
    if not f:
        flash('No file uploaded', 'error')
        return redirect(url_for('main.opportunities'))
    try:
        data = f.read().decode('utf-8')
    except Exception:
        flash('Failed to read uploaded file (ensure UTF-8 CSV)', 'error')
        return redirect(url_for('main.opportunities'))

    reader = csv.DictReader(io.StringIO(data))
    created = 0
    errors = []
    for idx, row in enumerate(reader, start=1):
        name = (row.get('name') or row.get('Name') or '').strip()
        account_name = (row.get('account') or row.get('company') or '').strip()
        if not name or not account_name:
            errors.append(f'Row {idx}: missing name or account')
            continue
        account = Account.query.filter_by(name=account_name).first()
        if not account:
            errors.append(f'Row {idx}: account "{account_name}" not found')
            continue
        owner = None
        owner_email = (row.get('owner_email') or row.get('owner') or '').strip()
        if owner_email:
            owner = User.query.filter_by(email=owner_email).first()
        try:
            close_date = None
            if row.get('close_date'):
                close_date = datetime.strptime(row.get('close_date'), '%Y-%m-%d')
            opp = Opportunity(
                name=name,
                stage=row.get('stage') or 'Prospecting',
                value=int(row.get('value')) if row.get('value') else None,
                close_date=close_date,
                account_id=account.id,
                owner_id=owner.id if owner else None
            )
            db.session.add(opp)
            db.session.commit()
            created += 1
        except Exception as e:
            db.session.rollback()
            errors.append(f'Row {idx}: DB error: {e}')

    _audit_event('import.opportunities', current_user.id if current_user.is_authenticated else None, {'created': created, 'errors': len(errors)})
    return render_template('accounts/import_result.html', created=created, errors=errors, title='Opportunities Import Results')


@main.route('/api/dashboard')
@login_required
def api_dashboard():
    """Return JSON summary for dashboard widgets."""
    total_accounts = Account.query.count()
    total_contacts = Contact.query.count()
    total_opps = Opportunity.query.count()
    stages = {}
    for o in Opportunity.query.with_entities(Opportunity.stage).all():
        stages[o.stage] = stages.get(o.stage, 0) + 1
    # recent audit
    recent_audit = []
    try:
        inst = Path(current_app.instance_path)
        log_file = inst / 'audit.log'
        if log_file.exists():
            with log_file.open(encoding='utf-8') as f:
                lines = f.readlines()[-20:]
                for ln in reversed(lines):
                    try:
                        ev = json.loads(ln)
                        recent_audit.append(ev)
                    except Exception:
                        continue
    except Exception:
        current_app.logger.exception('Failed to read audit log')

    return {
        'total_accounts': total_accounts,
        'total_contacts': total_contacts,
        'total_opps': total_opps,
        'stages': stages,
        'recent_audit': recent_audit
    }


@main.route('/accounts/create', methods=['GET', 'POST'])
@login_required
def account_create():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Name is required', 'error')
            return render_template('accounts/form.html', title='Create Account')
        if Account.query.filter_by(name=name).first():
            flash('An account with this name already exists', 'error')
            return render_template('accounts/form.html', title='Create Account')

        account = Account(
            name=name,
            industry=request.form.get('industry'),
            phone=request.form.get('phone'),
            website=request.form.get('website'),
            owner_id=int(request.form.get('owner_id')) if request.form.get('owner_id') else None
        )
        db.session.add(account)
        db.session.commit()
        _audit_event('account.create', current_user.id if current_user.is_authenticated else None, {'account_id': account.id, 'name': account.name})
        flash('Account created successfully', 'success')
        return redirect(url_for('main.accounts'))

    users = User.query.order_by(User.first_name.asc()).all()
    return render_template('accounts/form.html', users=users, title='Create Account')


@main.route('/accounts/<int:account_id>')
@login_required
def account_detail(account_id):
    account = db.session.get(Account, account_id)
    if not account:
        abort(404)
    # fetch related contacts and opportunities
    contacts = account.contacts.order_by(Contact.id.desc()).limit(50).all()
    opportunities = account.opportunities.order_by(Opportunity.close_date.asc()).limit(50).all()
    return render_template('accounts/detail.html', account=account, contacts=contacts, opportunities=opportunities, title=account.name)


@main.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
def account_edit(account_id):
    account = db.session.get(Account, account_id)
    if not account:
        abort(404)
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Name is required', 'error')
            return render_template('accounts/form.html', account=account, title='Edit Account')
        account.name = name
        account.industry = request.form.get('industry')
        account.phone = request.form.get('phone')
        account.website = request.form.get('website')
        account.owner_id = int(request.form.get('owner_id')) if request.form.get('owner_id') else None
        db.session.commit()
        _audit_event('account.update', current_user.id if current_user.is_authenticated else None, {'account_id': account.id})
        flash('Account updated successfully', 'success')
        return redirect(url_for('main.account_detail', account_id=account.id))

    users = User.query.order_by(User.first_name.asc()).all()
    return render_template('accounts/form.html', account=account, users=users, title='Edit Account')


@main.route('/accounts/<int:account_id>/delete', methods=['POST'])
@login_required
def account_delete(account_id):
    account = db.session.get(Account, account_id)
    if not account:
        abort(404)
    # Only allow owner or admin to delete
    if account.owner_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to delete this account', 'error')
        return redirect(url_for('main.accounts'))
    db.session.delete(account)
    db.session.commit()
    _audit_event('account.delete', current_user.id if current_user.is_authenticated else None, {'account_id': account_id})
    flash('Account deleted successfully', 'success')
    return redirect(url_for('main.accounts'))

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