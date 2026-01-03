#!/usr/bin/env python3
"""Script to create a user for testing."""
import sys
from app.database import SessionLocal, init_db
from app.models.user import User
from app.utils.password import hash_password

def create_user(username: str, password: str):
    """Create a new user."""
    init_db()
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"User '{username}' already exists!")
            return
        
        # Create user
        user = User(
            username=username,
            password_hash=hash_password(password)
        )
        db.add(user)
        db.commit()
        print(f"User '{username}' created successfully!")
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <password>")
        sys.exit(1)
    
    create_user(sys.argv[1], sys.argv[2])

