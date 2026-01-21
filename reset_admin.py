#!/usr/bin/env python3
"""Reset Admin Password Script

Use this script if you can't login with the default credentials.
This will reset the admin password to: 784577
"""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.local_db import LocalDatabase
from utils.security import hash_password

def reset_admin():
    """Reset admin password to default"""
    try:
        db = LocalDatabase()
        db.initialize()
        
        default_username = "david"
        default_password = "784577"
        default_role = "admin"
        
        print(f"Checking for user '{default_username}'...")
        
        existing = db.get_user_by_username(default_username)
        
        if existing:
            print(f"✓ User '{default_username}' exists")
            print(f"Resetting password to: {default_password}")
            
            # Update with correct hash
            db.create_or_update_user(
                existing['id'],
                default_username,
                hash_password(default_password),
                default_role
            )
            print(f"✓ Password reset successfully!")
        else:
            print(f"User '{default_username}' not found. Creating...")
            user_id = str(uuid.uuid4())
            db.create_or_update_user(
                user_id,
                default_username,
                hash_password(default_password),
                default_role
            )
            print(f"✓ Admin user created!")
        
        print(f"\n=== Login Credentials ===")
        print(f"Username: {default_username}")
        print(f"Password: {default_password}")
        print(f"========================\n")
        
        db.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("\n=== NEXUZY ARTICAL - Admin Password Reset ===")
    print("This will reset the admin password to the default.\n")
    
    if reset_admin():
        print("Success! You can now login with the credentials above.")
        input("\nPress Enter to exit...")
    else:
        print("Failed to reset password. Check error messages above.")
        input("\nPress Enter to exit...")
