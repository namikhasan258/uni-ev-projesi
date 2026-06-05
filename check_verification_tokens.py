#!/usr/bin/env python3
"""
Diagnostic script to check verification tokens in the database
"""
import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('uniev.db')
cursor = conn.cursor()

print("=" * 80)
print("VERIFICATION TOKEN DIAGNOSTIC")
print("=" * 80)
print()

# Check all users with verification tokens
cursor.execute("""
    SELECT 
        id,
        email,
        first_name,
        last_name,
        is_verified,
        email_verification_token,
        email_verification_code_expires,
        created_at
    FROM users
    ORDER BY created_at DESC
    LIMIT 10
""")

users = cursor.fetchall()

print(f"Found {len(users)} recent users:")
print()

for user in users:
    user_id, email, first_name, last_name, is_verified, token, expires, created_at = user
    
    print(f"User ID: {user_id}")
    print(f"Email: {email}")
    print(f"Name: {first_name} {last_name}")
    print(f"Verified: {'✅ Yes' if is_verified else '❌ No'}")
    print(f"Created: {created_at}")
    
    if token:
        print(f"Token: {token[:30]}... (length: {len(token)})")
        print(f"Token Expires: {expires}")
        
        # Check if token is expired
        if expires:
            try:
                expires_dt = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                now = datetime.utcnow()
                if expires_dt < now:
                    print(f"⏰ Token EXPIRED (expired {(now - expires_dt).total_seconds() / 3600:.1f} hours ago)")
                else:
                    print(f"✅ Token VALID (expires in {(expires_dt - now).total_seconds() / 3600:.1f} hours)")
            except:
                print(f"⚠️ Could not parse expiry date")
    else:
        print("Token: None")
    
    print("-" * 80)
    print()

# Check for the specific token from the logs
specific_token = "Vw17Gs8a2nCdrDZVjtbNLrvxFPHH9FUqj6GSoxBYoys"
print(f"Searching for specific token: {specific_token}")
cursor.execute("""
    SELECT id, email, is_verified, email_verification_token
    FROM users
    WHERE email_verification_token = ?
""", (specific_token,))

result = cursor.fetchone()
if result:
    print(f"✅ FOUND: User ID {result[0]}, Email: {result[1]}, Verified: {result[2]}")
    print(f"   Full token: {result[3]}")
else:
    print(f"❌ NOT FOUND in database")
    print()
    print("Checking for partial matches...")
    cursor.execute("""
        SELECT id, email, email_verification_token
        FROM users
        WHERE email_verification_token LIKE ?
    """, (f"%{specific_token[:20]}%",))
    
    partial_results = cursor.fetchall()
    if partial_results:
        print(f"Found {len(partial_results)} partial matches:")
        for r in partial_results:
            print(f"  - User {r[0]} ({r[1]}): {r[2][:50]}...")
    else:
        print("No partial matches found either")

conn.close()

print()
print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
