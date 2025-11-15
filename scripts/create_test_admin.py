#!/usr/bin/env python
"""
Script to create a test admin user for the CRM application.
This allows testing the React front-end with backend integration.

Usage:
    python scripts/create_test_admin.py
"""

import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

def main():
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if admin user exists
        admin_email = 'admin@roshtech.com'
        admin_password = 'password123'
        
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin:
            print(f"Admin user already exists: {admin_email}")
            print("Resetting password to: password123")
            existing_admin.set_password(admin_password)
            db.session.commit()
        else:
            # Create new admin user
            admin = User(
                email=admin_email,
                first_name='Admin',
                last_name='User',
                role='owner'
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin user created successfully!")
        
        # Create sample test user
        test_email = 'testuser@roshtech.com'
        test_password = 'password123'
        
        existing_test = User.query.filter_by(email=test_email).first()
        if existing_test:
            print(f"Test user already exists: {test_email}")
        else:
            test_user = User(
                email=test_email,
                first_name='Test',
                last_name='User',
                role='sales'
            )
            test_user.set_password(test_password)
            db.session.add(test_user)
            db.session.commit()
            print(f"✓ Test user created successfully!")
        
        print("\n" + "="*60)
        print("TEST CREDENTIALS")
        print("="*60)
        print(f"Admin Account:")
        print(f"  Email:    {admin_email}")
        print(f"  Password: {admin_password}")
        print(f"  Role:     owner")
        print()
        print(f"Test Account:")
        print(f"  Email:    {test_email}")
        print(f"  Password: {test_password}")
        print(f"  Role:     sales")
        print("="*60)

if __name__ == '__main__':
    main()
