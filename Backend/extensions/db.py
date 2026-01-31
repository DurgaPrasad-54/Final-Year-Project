from pymongo import MongoClient, ASCENDING, DESCENDING
from config import Config
import logging

logger = logging.getLogger(__name__)

client = MongoClient(Config.MONGO_URI)
db = client.get_database()

# ===== CREATE INDEXES FOR FASTER QUERIES =====
def ensure_indexes():
    """Create database indexes for optimal query performance"""
    try:
        # Index for chats collection - speeds up list and history queries
        db.chats.create_index([("userId", ASCENDING), ("updatedAt", DESCENDING)])
        db.chats.create_index([("userId", ASCENDING), ("chatId", ASCENDING)])
        db.chats.create_index([("userId", ASCENDING), ("totalMessages", ASCENDING)])
        
        # Index for users collection
        db.users.create_index([("email", ASCENDING)], unique=True)
        
        logger.info("✓ Database indexes created/verified")
    except Exception as e:
        logger.warning(f"Could not create indexes: {e}")

# Create indexes on module load
ensure_indexes()
