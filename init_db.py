#!/usr/bin/env python3
"""
Script to initialize database and create tables
"""

import sys
import os
sys.path.append(os.getcwd())

from app import db, app, User

def initialize_database():
    print("Initializing database...")

    with app.app_context():
        # Create all tables
        db.create_all()
        print("All tables created successfully!")

        # Check if admin user already exists, if not create one
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created (username: admin, password: admin)")
        else:
            print("Admin user already exists")

    print("Database initialization completed!")

if __name__ == "__main__":
    initialize_database()