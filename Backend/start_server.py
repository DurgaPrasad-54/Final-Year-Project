#!/usr/bin/env python3
"""
Simple script to start the backend server with proper error handling
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    try:
        import flask
        logger.info("✓ Flask installed")
    except ImportError:
        logger.error("✗ Flask not installed")
        return False
    
    try:
        import pymongo
        logger.info("✓ PyMongo installed")
    except ImportError:
        logger.error("✗ PyMongo not installed")
        return False
    
    try:
        import flask_cors
        logger.info("✓ Flask-CORS installed")
    except ImportError:
        logger.error("✗ Flask-CORS not installed")
        return False
    
    try:
        import torch
        logger.info("✓ PyTorch installed")
    except ImportError:
        logger.error("✗ PyTorch not installed - Model won't load")
    
    try:
        import transformers
        logger.info("✓ Transformers installed")
    except ImportError:
        logger.error("✗ Transformers not installed - Model won't load")
    
    return True

def check_mongodb():
    """Check if MongoDB is running"""
    logger.info("Checking MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.server_info()  # Will raise exception if cannot connect
        logger.info("✓ MongoDB is running on localhost:27017")
        client.close()
        return True
    except Exception as e:
        logger.warning(f"⚠ MongoDB connection failed: {e}")
        logger.warning("  Make sure MongoDB is running: mongod")
        return False

def check_files():
    """Check if required files exist"""
    logger.info("Checking required files...")
    
    files_to_check = [
        "./ai/tinyllama_model/config.json",
        "./data/medical_final_dataset.json",
        "./ai/index.faiss",
        "./ai/embeddings.npy"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            logger.info(f"✓ {file_path}")
        else:
            logger.warning(f"⚠ {file_path} - File not found")
            all_exist = False
    
    return all_exist

def start_server():
    """Start the Flask server"""
    logger.info("\n" + "="*60)
    logger.info("Starting Medical ChatBot Backend")
    logger.info("="*60 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Missing critical dependencies. Please install them:")
        logger.error("pip install -r requirements.txt")
        return False
    
    logger.info()
    
    # Check MongoDB
    mongodb_ok = check_mongodb()
    
    logger.info()
    
    # Check files
    files_ok = check_files()
    
    if not files_ok:
        logger.warning("\n⚠ Some AI files are missing - Chat will be limited")
    
    logger.info("\n" + "="*60)
    logger.info("Starting Flask server...")
    logger.info("="*60 + "\n")
    
    try:
        from app import app
        logger.info("✓ App imported successfully")
        logger.info("\n🚀 Server starting on http://localhost:5000")
        logger.info("📝 Logs: medchat.log")
        logger.info("\nPress Ctrl+C to stop\n")
        
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"\n🚀 Server starting on http://localhost:{port}")
        app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)
        
    except Exception as e:
        logger.error(f"✗ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = start_server()
    sys.exit(0 if success else 1)
