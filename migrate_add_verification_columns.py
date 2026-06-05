#!/usr/bin/env python3
"""
Migration script to add email_verification_code and password_reset_code columns
to the users table if they don't exist.
"""

import sqlite3
import os

# Database path
DB_PATH = "uniev.db"

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate():
    """Add missing columns to users table"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check and add email_verification_code
        if not column_exists(cursor, "users", "email_verification_code"):
            print("➕ Adding email_verification_code column...")
            cursor.execute("ALTER TABLE users ADD COLUMN email_verification_code TEXT")
            print("✅ Added email_verification_code")
        else:
            print("✓ email_verification_code already exists")
        
        # Check and add email_verification_code_expires (IMPORTANT: This was missing!)
        if not column_exists(cursor, "users", "email_verification_code_expires"):
            print("➕ Adding email_verification_code_expires column...")
            cursor.execute("ALTER TABLE users ADD COLUMN email_verification_code_expires DATETIME")
            print("✅ Added email_verification_code_expires")
        else:
            print("✓ email_verification_code_expires already exists")
        
        # Check and add password_reset_code
        if not column_exists(cursor, "users", "password_reset_code"):
            print("➕ Adding password_reset_code column...")
            cursor.execute("ALTER TABLE users ADD COLUMN password_reset_code TEXT")
            print("✅ Added password_reset_code")
        else:
            print("✓ password_reset_code already exists")
        
        # Check and add password_reset_code_expires
        if not column_exists(cursor, "users", "password_reset_code_expires"):
            print("➕ Adding password_reset_code_expires column...")
            cursor.execute("ALTER TABLE users ADD COLUMN password_reset_code_expires DATETIME")
            print("✅ Added password_reset_code_expires")
        else:
            print("✓ password_reset_code_expires already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...\n")
    success = migrate()
    if success:
        print("\n🎉 Database is now up to date!")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
