from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from extensions.jwt import jwt
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from datetime import datetime
import logging
import sys
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('medchat.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
logger.info(f"Configuration loaded: {Config.__name__}")

# Enable CORS with proper configuration for streaming
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000", "*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "Cache-Control"],
        "expose_headers": ["Content-Type", "Authorization", "X-Accel-Buffering"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

logger.info("CORS enabled")

jwt.init_app(app)
logger.info("JWT initialized")

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)
logger.info("Blueprints registered")

# Global error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad request",
        "message": str(error.description) if hasattr(error, 'description') else "Invalid request",
        "timestamp": datetime.utcnow().isoformat()
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "error": "Unauthorized",
        "message": "Authentication required. Please provide a valid JWT token.",
        "timestamp": datetime.utcnow().isoformat()
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "error": "Forbidden",
        "message": "You don't have permission to access this resource",
        "timestamp": datetime.utcnow().isoformat()
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not found",
        "message": "The requested resource was not found",
        "timestamp": datetime.utcnow().isoformat()
    }), 404

@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        "error": "Unprocessable entity",
        "message": str(error.description) if hasattr(error, 'description') else "Invalid data",
        "timestamp": datetime.utcnow().isoformat()
    }), 422

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}", exc_info=True)
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later.",
        "timestamp": datetime.utcnow().isoformat()
    }), 500

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "Medical Chatbot API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


# Model status endpoint
@app.route("/status", methods=["GET"])
def model_status():
    """Check if Groq API and RAG are ready"""
    try:
        from services.medchat_gemini import get_groq_client
        from services.rag_service import _initialized as rag_initialized, _faiss_index, _chunks
        
        client = get_groq_client()
        
        rag_status = {
            "initialized": rag_initialized,
            "index_size": _faiss_index.ntotal if _faiss_index else 0,
            "chunks_count": len(_chunks) if _chunks else 0
        }
        
        return jsonify({
            "status": "ready",
            "service": "Groq API (Llama 3.3) + RAG",
            "message": "Ready for fast medical responses with context retrieval",
            "rag": rag_status,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# API info endpoint
@app.route("/api/info", methods=["GET"])
def api_info():
    """Get API information"""
    return jsonify({
        "name": "Medical Chatbot API",
        "version": "1.0.0",
        "description": "Real-time medical chatbot with RAG (Retrieval Augmented Generation)",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "profile": "GET /auth/profile",
                "update": "PUT /auth/update-profile"
            },
            "chat": {
                "ask": "POST /chat/ask",
                "history": "GET /chat/history",
                "recent": "GET /chat/recent",
                "search": "GET /chat/search",
                "stats": "GET /chat/stats",
                "clear": "DELETE /chat/clear",
                "delete": "DELETE /chat/delete-exchange"
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# Request/Response logging middleware
@app.before_request
def log_request():
    logger.debug(f"Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    logger.debug(f"Response: {response.status_code} {request.path}")
    return response


# ===== GROQ CLIENT & RAG WARMUP ON STARTUP =====
def warmup_models():
    """Preload Groq client and RAG index in background thread for instant responses"""
    try:
        logger.info("[WARMUP] Starting Groq client warmup in background...")
        from services.medchat_gemini import get_groq_client
        
        # Initialize client
        client = get_groq_client()
        logger.info("[OK] Groq client initialized successfully")
        
        # Initialize RAG system
        logger.info("[WARMUP] Initializing RAG system...")
        from services.rag_service import init_rag
        rag_ready = init_rag()
        if rag_ready:
            logger.info("[OK] RAG system with FAISS + MiniLM initialized successfully")
        else:
            logger.warning("[WARN] RAG system not available - running without context retrieval")
        
        logger.info("[READY] Server is ready for FAST responses!")
    except Exception as e:
        logger.error(f"Model warmup error: {e}")


# Start warmup in background thread on first request
_warmup_started = False

@app.before_request
def start_warmup():
    """Start model warmup on first request (not blocking)"""
    global _warmup_started
    if not _warmup_started:
        _warmup_started = True
        warmup_thread = threading.Thread(target=warmup_models, daemon=True)
        warmup_thread.start()
        logger.info("[INFO] Model warmup thread started")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Medical Chatbot API Server")
    logger.info("=" * 60)
    logger.info(f"Host: 0.0.0.0")
    logger.info(f"Port: 5000")
    logger.info(f"Debug: True")
    logger.info("=" * 60)
    
    # Start warmup immediately when running directly
    warmup_thread = threading.Thread(target=warmup_models, daemon=True)
    warmup_thread.start()
    
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
