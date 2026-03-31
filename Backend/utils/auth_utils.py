import bcrypt

def hash_password(password):
    """Hash password - returns string for safe MongoDB storage"""
    try:
        hash_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Convert bytes to string for MongoDB storage
        return hash_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Password hashing failed: {str(e)}")

def verify_password(password, hashed):
    """Verify password against hash - handles both string and bytes"""
    try:
        # Ensure password is bytes
        password_bytes = password.encode('utf-8')
        
        # Convert hashed to bytes if it's a string
        if isinstance(hashed, str):
            hashed_bytes = hashed.encode('utf-8')
        else:
            hashed_bytes = hashed
        
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        return False
