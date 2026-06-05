#!/usr/bin/env python3
"""
Check database schema for users table
"""
import sqlite3

conn = sqlite3.connect('uniev.db')
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

print("=" * 80)
print("USERS TABLE SCHEMA")
print("=" * 80)
print()

for col in columns:
    col_id, name, col_type, not_null, default_val, pk = col
    print(f"{name:40} {col_type:15} {'NOT NULL' if not_null else ''} {'PK' if pk else ''}")

print()
print("=" * 80)

# Now check for verification-related columns
print()
print("VERIFICATION-RELATED COLUMNS:")
print()

verification_cols = [col for col in columns if 'verif' in col[1].lower() or 'token' in col[1].lower()]
for col in verification_cols:
    print(f"  - {col[1]}")

conn.close()
