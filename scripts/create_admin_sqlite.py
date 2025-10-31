#!/usr/bin/env python3
"""
Create or update the admin user directly in the project's SQLite DB.

This script uses only the Python standard library to compute a PBKDF2-HMAC-SHA256
password hash in the same format Werkzeug uses (pbkdf2:sha256:iterations$salt$hash).

Run from the project root like:
    python scripts/create_admin_sqlite.py --email admin@test.com --password password123

This avoids needing to install Flask/Werkzeug when pip access is not available.
"""
import os
import sqlite3
import argparse
import secrets
import hashlib


def generate_pbkdf2_sha256_hash(password: str, iterations: int = 260000, salt_len: int = 8) -> str:
    """Return a Werkzeug-compatible PBKDF2-SHA256 hash string.

    Format: pbkdf2:sha256:<iterations>$<salt>$<hex>
    """
    # generate a salt (hex string)
    salt = secrets.token_hex(salt_len)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
    hex_hash = dk.hex()
    return f"pbkdf2:sha256:{iterations}${salt}${hex_hash}"


def ensure_admin(db_path: str, email: str, password: str, first_name: str = 'Test', last_name: str = 'Admin'):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    pwd_hash = generate_pbkdf2_sha256_hash(password)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Ensure the user table exists and has expected columns. We perform a simple upsert.
    cur.execute("SELECT id FROM user WHERE email = ?", (email,))
    row = cur.fetchone()
    if row:
        user_id = row[0]
        cur.execute(
            "UPDATE user SET password_hash = ?, first_name = ?, last_name = ?, role = ? WHERE id = ?",
            (pwd_hash, first_name, last_name, 'admin', user_id),
        )
        print(f"Updated admin user (id={user_id}) with email: {email}")
    else:
        cur.execute(
            "INSERT INTO user (email, password_hash, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)",
            (email, pwd_hash, first_name, last_name, 'admin'),
        )
        print(f"Created admin user with email: {email}")

    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='app.db', help='Path to SQLite database (default: app.db)')
    parser.add_argument('--email', default='admin@test.com', help='Admin email')
    parser.add_argument('--password', default='password123', help='Admin password')
    parser.add_argument('--first', default='Test', help='First name')
    parser.add_argument('--last', default='Admin', help='Last name')
    args = parser.parse_args()

    db_path = os.path.abspath(args.db)
    try:
        ensure_admin(db_path, args.email, args.password, args.first, args.last)
        print(f"Admin credentials: {args.email} / {args.password}")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == '__main__':
    main()
