#!/usr/bin/env python3
"""
Script to properly initialize database with all tables
"""

import sys
import os
sys.path.append(os.getcwd())

from app import db, app

def main():
    print("Creating all tables in database...")
    
    with app.app_context():
        # Reflect the current state and create tables
        db.create_all()
        print("Tables created successfully!")
        
        # Verify tables were created
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {tables}")
        
        # Show table structure for verification
        for table_name in tables:
            print(f"\nTable: {table_name}")
            columns = inspector.get_columns(table_name)
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")

if __name__ == "__main__":
    main()