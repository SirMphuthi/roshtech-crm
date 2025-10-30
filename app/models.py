from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# This is the callback function that Flask-Login will use to load a user
# from the session. It must be defined to use Flask-Login.
@login_manager.user_loader
def load_user(user_id):
    # Use session.get to avoid SQLAlchemy Query.get() deprecation warnings
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        # fallback
        return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """
    Model for internal CRM users (your team).
    UserMixin provides required methods for Flask-Login (is_authenticated, etc.).
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(20), default='user') # (e.g., 'admin', 'sales')
    
    # Relationships
    # This user (e.g., a sales rep) might own several accounts
    accounts = db.relationship('Account', back_populates='owner', lazy=True)
    opportunities = db.relationship('Opportunity', back_populates='owner', lazy=True)
    tokens = db.relationship('Token', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Token(db.Model):
    """API token for programmatic access.
    Tokens are simple bearer tokens tied to a User and can be revoked.
    """
    id = db.Column(db.Integer, primary_key=True)
    # We store a hashed token and a short prefix (first 8 chars) for quick lookup.
    token_hash = db.Column(db.String(256), nullable=False)
    token_prefix = db.Column(db.String(16), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    scopes = db.Column(db.String(255), nullable=True)
    revoked = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='tokens')

    def set_token(self, plain_token: str):
        self.token_hash = generate_password_hash(plain_token)
        # store short prefix for indexed lookup (helps avoid scanning all tokens)
        self.token_prefix = plain_token[:8]

    def check_token(self, plain_token: str) -> bool:
        if self.revoked:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return check_password_hash(self.token_hash, plain_token)

    def revoke(self):
        self.revoked = True
        db.session.commit()

    def __repr__(self):
        return f'<Token {self.token_prefix}... for user_id={self.user_id}>'

class Account(db.Model):
    """
    Model for a company/organization you do business with.
    (e.g., Gauteng Dept. of Safety, a logistics client, a property group)
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    industry = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key for the User who "owns" or manages this account
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    owner = db.relationship('User', back_populates='accounts')
    contacts = db.relationship('Contact', back_populates='account', lazy='dynamic', cascade="all, delete-orphan")
    opportunities = db.relationship('Opportunity', back_populates='account', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Account {self.name}>'

class Contact(db.Model):
    """
    Model for individuals who work at an Account.
    """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True)
    phone_number = db.Column(db.String(20))
    role_title = db.Column(db.String(100)) # (e.g., "Head of Security", "Logistics Manager")
    
    # Foreign key to link this contact to a company
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    
    # Relationships
    account = db.relationship('Account', back_populates='contacts')

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'

class Opportunity(db.Model):
    """
    Model for a potential deal or project.
    This can be for any RoshTech division (CPS, Logistics, etc.)
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    stage = db.Column(db.String(50), default='Prospecting') # (e.g., Prospecting, Proposal, Closed-Won, Closed-Lost)
    value = db.Column(db.Integer) # Estimated value of the deal
    close_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to link this deal to a company
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    # Foreign key for the User who is managing this deal
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    account = db.relationship('Account', back_populates='opportunities')
    owner = db.relationship('User', back_populates='opportunities')

    def __repr__(self):
        return f'<Opportunity {self.name}>'
