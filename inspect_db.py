#!/usr/bin/env python3
"""
Script to inspect the database contents
"""

import sqlite3
import json
from datetime import datetime
import os

def inspect_database():
    # Use the same database path as in app.py
    db_path = 'industrial_analysis.db'

    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' does not exist!")
        return

    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    cursor = conn.cursor()

    print("=== Database Inspection ===")

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in database: {[table[0] for table in tables]}")

    print("\n" + "="*50)

    # Check users table
    if 'user' in [table[0] for table in tables]:
        print("Users table:")
        cursor.execute("SELECT * FROM user;")
        users = cursor.fetchall()
        for user in users:
            print(f"  ID: {user['id']}, Username: {user['username']}, Role: {user['role']}")

    print("\n" + "="*50)

    # Check reports table
    if 'report' in [table[0] for table in tables]:
        print("Reports table:")
        cursor.execute("SELECT * FROM report;")
        reports = cursor.fetchall()
        for report in reports:
            print(f"  ID: {report['id']}, Report ID: {report['report_id']}, Title: {report['title'][:50]}...")

    print("\n" + "="*50)

    # Check wechat_articles table (if it exists)
    if 'wechat_articles' in [table[0] for table in tables]:
        print("WeChat Articles table:")
        cursor.execute("SELECT COUNT(*) as count FROM wechat_articles;")
        count = cursor.fetchone()['count']
        print(f"  Total articles: {count}")

        if count > 0:
            # Show some sample articles
            cursor.execute("SELECT * FROM wechat_articles LIMIT 5;")
            articles = cursor.fetchall()
            for article in articles:
                print(f"  ID: {article['id']}")
                print(f"    Title: {article['title'][:50]}...")
                print(f"    Source: {article['source_account']}")
                print(f"    Date: {article['publish_date']}")
                print(f"    Summary: {article['summary'][:100]}...")
                print(f"    Keywords: {article['keywords']}")
                print(f"    Created: {article['created_at']}")
                print()
        else:
            print("  WeChat Articles table exists but is currently empty")
            print("  This is expected if wechatsogou is not installed or no scraping has run yet")
    else:
        print("WeChat Articles table does not exist yet")
        print("This might be because database was not properly initialized with Flask-SQLAlchemy")

    print("\n" + "="*50)

    # Show table structure
    for table in tables:
        table_name = table[0]
        print(f"\nStructure of '{table_name}' table:")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - Default: {col[4]}")

    # Close connection
    conn.close()

if __name__ == "__main__":
    inspect_database()