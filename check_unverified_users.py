#!/usr/bin/env python3
"""
Check for unverified users
"""
import sqlite3

conn = sqlite3.connect('uniev.db')
cursor = conn.cursor()

print("=" * 80)
print("UNVERIFIED USERS")
print("=" * 80)
print()

# Check for unverified users
cursor.execute("""
    SELECT 
        id,
        email,
        first_name,
        is_verified,
        email_verification_token,
        created_at
    FROM users
    WHERE is_verified = 0
    ORDER BY created_at DESC
""")

users = cursor.fetchall()

if len(users) == 0:
    print("✅ No unverified users found")
    print()
    print("All users in the database are verified.")
else:
    print(f"Found {len(users)} unverified users:")
    print()
    
    for user in users:
        user_id, email, first_name, is_verified, token, created_at = user
        
        print(f"User: {first_name} ({email})")
        print(f"  ID: {user_id}")
        print(f"  Created: {created_at}")
        
        if token:
            print(f"  Token: {token[:40]}...")
        else:
            print(f"  Token: ⚠️ MISSING! (This user cannot verify)")
        
        print()

# Check for the specific email from logs
print("=" * 80)
print("Checking for dohoc66378@inreur.com:")
print()

cursor.execute("""
    SELECT id, email, first_name, is_verified, email_verification_token, created_at
    FROM users
    WHERE email = ?
""", ("dohoc66378@inreur.com",))

result = cursor.fetchone()
if result:
    user_id, email, first_name, is_verified, token, created_at = result
    print(f"✅ User found:")
    print(f"   ID: {user_id}")
    print(f"   Name: {first_name}")
    print(f"   Verified: {'✅ Yes' if is_verified else '❌ No'}")
    print(f"   Created: {created_at}")
    if token:
        print(f"   Token: {token}")
    else:
        print(f"   Token: None")
else:
    print(f"❌ User not found in database")
    print()
    print("This user may have been deleted or never registered successfully.")

conn.close()

print()
print("=" * 80)
