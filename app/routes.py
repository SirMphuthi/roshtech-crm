from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Account, Opportunity

# A Blueprint is a way to organize a group of related routes.
# We call it 'main' here.
main = Blueprint('main', __name__)

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
