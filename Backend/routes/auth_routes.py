from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.user_model import users_collection
from utils.auth_utils import hash_password, verify_password
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Email validation regex
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def is_valid_email(email):
    """Validate email format"""
    return re.match(EMAIL_REGEX, email) is not None

def is_valid_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 128:
        return False, "Password is too long"
    return True, "Valid"

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        name = data.get("name", "").strip()

        # Validation
        if not email:
            return jsonify({"error": "Email is required"}), 400

        if not is_valid_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        if not password:
            return jsonify({"error": "Password is required"}), 400

        is_valid, message = is_valid_password(password)
        if not is_valid:
            return jsonify({"error": message}), 400

        # Check if user already exists
        if users_collection.find_one({"email": email}):
            return jsonify({"error": "User with this email already exists"}), 409

        # Create user
        user_doc = {
            "email": email,
            "password": hash_password(password),
            "name": name or email.split("@")[0],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "isActive": True
        }

        result = users_collection.insert_one(user_doc)
        logger.info(f"New user registered: {email}")

        return jsonify({
            "message": "Registration successful",
            "email": email,
            "userId": str(result.inserted_id),
            "timestamp": datetime.utcnow().isoformat()
        }), 201

    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        return jsonify({
            "error": "Registration failed",
            "message": str(e)
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        # Validation
        if not email:
            return jsonify({"error": "Email is required"}), 400

        if not password:
            return jsonify({"error": "Password is required"}), 400

        # Find user
        user = users_collection.find_one({"email": email})

        if not user or not verify_password(password, user["password"]):
            logger.warning(f"Failed login attempt for {email}")
            return jsonify({"error": "Invalid email or password"}), 401

        # Check if user is active
        if not user.get("isActive", True):
            return jsonify({"error": "Account is inactive"}), 403

        # Create JWT token
        access_token = create_access_token(identity=str(user["_id"]))
        
        # Update last login
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"lastLogin": datetime.utcnow()}}
        )

        logger.info(f"User logged in: {email}")

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "Bearer",
            "userId": str(user["_id"]),
            "email": email,
            "name": user.get("name", email.split("@")[0]),
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({
            "error": "Login failed",
            "message": str(e)
        }), 500


@auth_bp.route("/verify-token", methods=["GET"])
def verify_token():
    """Verify if a token is valid (optional, useful for frontend)"""
    from flask_jwt_extended import jwt_required, get_jwt_identity
    
    try:
        # This will fail if token is invalid
        @jwt_required()
        def _verify():
            user_id = get_jwt_identity()
            user = users_collection.find_one({"_id": user_id})
            return user is not None

        # Call the decorated function
        return _verify()
    except Exception as e:
        return jsonify({"error": "Invalid token"}), 401


@auth_bp.route("/profile", methods=["GET"])
def get_profile():
    """Get user profile"""
    from flask_jwt_extended import jwt_required, get_jwt_identity
    
    try:
        @jwt_required()
        def _get_profile():
            user_id = get_jwt_identity()
            user = users_collection.find_one(
                {"_id": user_id},
                {"password": 0}  # Exclude password
            )
            
            if not user:
                return jsonify({"error": "User not found"}), 404

            return jsonify({
                "userId": str(user["_id"]),
                "email": user.get("email"),
                "name": user.get("name"),
                "createdAt": user.get("createdAt", datetime.utcnow()).isoformat(),
                "lastLogin": user.get("lastLogin", datetime.utcnow()).isoformat()
            }), 200

        return _get_profile()
    except Exception as e:
        logger.error(f"Error fetching profile: {str(e)}")
        return jsonify({
            "error": "Failed to fetch profile",
            "message": str(e)
        }), 500


@auth_bp.route("/update-profile", methods=["PUT"])
def update_profile():
    """Update user profile"""
    from flask_jwt_extended import jwt_required, get_jwt_identity
    
    try:
        @jwt_required()
        def _update_profile():
            user_id = get_jwt_identity()
            data = request.get_json() or {}
            
            update_data = {}
            
            if "name" in data:
                name = data.get("name", "").strip()
                if len(name) > 0 and len(name) <= 100:
                    update_data["name"] = name
            
            if not update_data:
                return jsonify({"error": "No valid fields to update"}), 400
            
            update_data["updatedAt"] = datetime.utcnow()
            
            result = users_collection.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return jsonify({"error": "User not found"}), 404
            
            logger.info(f"Profile updated for user {user_id}")
            
            return jsonify({
                "message": "Profile updated successfully",
                "timestamp": datetime.utcnow().isoformat()
            }), 200

        return _update_profile()
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({
            "error": "Failed to update profile",
            "message": str(e)
        }), 500

