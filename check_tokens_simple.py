#!/usr/bin/env python3
"""
Simple check for verification tokens
"""
import sqlite3

conn = sqlite3.connect('uniev.db')
cursor = conn.cursor()

print("=" * 80)
print("CHECKING VERIFICATION TOKENS")
print("=" * 80)
print()

# Check all users
cursor.execute("""
    SELECT 
        id,
        email,
        first_name,
        is_verified,
        email_verification_token,
        created_at
    FROM users
    ORDER BY created_at DESC
    LIMIT 10
""")

users = cursor.fetchall()

print(f"Found {len(users)} recent users:")
print()

for user in users:
    user_id, email, first_name, is_verified, token, created_at = user
    
    print(f"User: {first_name} ({email})")
    print(f"  ID: {user_id}")
    print(f"  Verified: {'✅ Yes' if is_verified else '❌ No'}")
    print(f"  Created: {created_at}")
    
    if token:
        print(f"  Token: {token[:40]}... (length: {len(token)})")
    else:
        print(f"  Token: None")
    
    print()

# Check for the specific token from the logs
specific_token = "Vw17Gs8a2nCdrDZVjtbNLrvxFPHH9FUqj6GSoxBYoys"
print("=" * 80)
print(f"Searching for specific token from logs:")
print(f"  {specific_token}")
print()

cursor.execute("""
    SELECT id, email, first_name, is_verified, email_verification_token
    FROM users
    WHERE email_verification_token = ?
""", (specific_token,))

result = cursor.fetchone()
if result:
    print(f"✅ FOUND IN DATABASE!")
    print(f"   User ID: {result[0]}")
    print(f"   Email: {result[1]}")
    print(f"   Name: {result[2]}")
    print(f"   Verified: {result[3]}")
    print(f"   Token: {result[4]}")
else:
    print(f"❌ NOT FOUND in database")
    print()
    print("This means the token in the email doesn't match any user in the database.")
    print("Possible causes:")
    print("  1. Token was not saved during registration")
    print("  2. Token was overwritten by a resend operation")
    print("  3. Database transaction was rolled back")
    print("  4. Wrong database file is being used")

conn.close()

print()
print("=" * 80)
