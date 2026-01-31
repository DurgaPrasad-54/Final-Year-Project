from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.chat_model import chats_collection
from services.medchat_gemini import (
    detect_intent,
    handle_question,
    stream_medical_answer,
    get_static_response,
    Intent,
)
from datetime import datetime
import logging
import json
import uuid

logger = logging.getLogger(__name__)
chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


# =======================
# CREATE NEW CHAT
# =======================
@chat_bp.route("/new", methods=["POST"])
@jwt_required()
def new_chat():
    """Create a new chat session with 0 messages"""
    try:
        user_id = get_jwt_identity()
        chat_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        chat_doc = {
            "userId": user_id,
            "chatId": chat_id,
            "messages": [],
            "createdAt": now,
            "updatedAt": now,
            "title": "New Chat",
            "totalMessages": 0
        }
        
        # Insert into database
        result = chats_collection.insert_one(chat_doc)
        logger.info(f"[OK] Created new chat {chat_id} for user {user_id} with 0 messages")
        
        return jsonify({
            "chatId": chat_id,
            "title": "New Chat",
            "messages": [],
            "totalMessages": 0,
            "createdAt": now.isoformat(),
            "message": "New chat created successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating new chat: {str(e)}")
        return jsonify({"error": "Failed to create chat"}), 500


# =======================
# ASK QUESTION
# =======================
@chat_bp.route("/ask", methods=["POST"])
@jwt_required()
def ask():
    """Ask a question - handles medical questions AND greetings"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        question = data.get("question", "").strip()
        chat_id = data.get("chatId", None)

        if not question:
            return jsonify({"error": "Question is required"}), 400

        if len(question) < 2:
            return jsonify({"error": "Question must be at least 2 characters"}), 400

        # 1️⃣ Detect intent using new service
        intent = detect_intent(question)
        question_type = intent.value
        
        # 2️⃣ Get or create chat session
        if chat_id:
            chat = chats_collection.find_one({"userId": user_id, "chatId": chat_id})
        else:
            chat = chats_collection.find_one({"userId": user_id}, sort=[("createdAt", -1)])

        if not chat:
            # Create new chat with question as title
            chat_id = str(uuid.uuid4())
            chat_title = question[:50] + "..." if len(question) > 50 else question
            chat_doc = {
                "userId": user_id,
                "chatId": chat_id,
                "messages": [],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                "title": chat_title,
                "totalMessages": 0
            }
            chats_collection.insert_one(chat_doc)
            chat = chat_doc
        else:
            chat_id = chat["chatId"]
            # Update title if it's still "New Chat" and this is first real message
            if chat.get("title") == "New Chat" and chat.get("totalMessages", 0) == 0:
                new_title = question[:50] + "..." if len(question) > 50 else question
                chats_collection.update_one(
                    {"userId": user_id, "chatId": chat_id},
                    {"$set": {"title": new_title}}
                )

        # 3️⃣ Generate response based on intent
        if intent != Intent.MEDICAL:
            # Handle non-medical intents (greeting, thanks, goodbye, identity, reject)
            answer = get_static_response(intent)
            context_used = False
        else:
            # Medical question - use Groq LLM
            history = chat.get("messages", [])[-3:]  # Last 3 messages for context
            answer = handle_question(question, history=history)
            context_used = True
            
            # Validate response
            if not answer or len(answer.strip()) < 5:
                answer = "I understand you're asking about a health topic. Could you please provide more details or rephrase your question? I'm here to help with medical information."

        # 4️⃣ Store messages in database
        chats_collection.update_one(
            {"userId": user_id, "chatId": chat_id},
            {
                "$push": {"messages": {"$each": [
                    {"role": "user", "content": question, "timestamp": datetime.utcnow()},
                    {"role": "assistant", "content": answer, "timestamp": datetime.utcnow(), "contextUsed": context_used}
                ]}},
                "$set": {"updatedAt": datetime.utcnow()},
                "$inc": {"totalMessages": 2}
            }
        )

        logger.info(f"Response generated for chat {chat_id} (type: {question_type})")

        return jsonify({
            "answer": answer,
            "chatId": chat_id,
            "timestamp": datetime.utcnow().isoformat(),
            "contextUsed": context_used,
            "questionType": question_type
        }), 200

    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to process question"}), 500


# =======================
# GET CHAT HISTORY (SPECIFIC CHAT)
# =======================
@chat_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    """Fetch chat history for a specific chat session"""
    try:
        user_id = get_jwt_identity()
        chat_id = request.args.get("chatId", None)
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 50, type=int)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 50
        
        # Get specific chat
        if chat_id:
            chat = chats_collection.find_one({"userId": user_id, "chatId": chat_id})
        else:
            # Get most recent chat
            chat = chats_collection.find_one({"userId": user_id}, sort=[("createdAt", -1)])
        
        if not chat:
            return jsonify({"error": "Chat not found"}), 404
        
        # Get all messages from this chat
        messages = chat.get("messages", [])
        total_messages = len(messages)
        
        # Paginate
        start_idx = (page - 1) * limit
        paginated_messages = messages[start_idx:start_idx + limit]
        
        # Convert timestamps to ISO format for JSON serialization
        for msg in paginated_messages:
            if "timestamp" in msg and hasattr(msg["timestamp"], 'isoformat'):
                msg["timestamp"] = msg["timestamp"].isoformat()
        
        return jsonify({
            "chatId": chat["chatId"],
            "title": chat.get("title", "Chat"),
            "messages": paginated_messages,
            "totalMessages": total_messages,
            "currentPage": page,
            "totalPages": (total_messages + limit - 1) // limit
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return jsonify({"error": "Failed to fetch history"}), 500


# =======================
# GET ALL CHATS (SUMMARY)
# =======================
@chat_bp.route("/list", methods=["GET"])
@jwt_required()
def list_chats():
    """Get list of all chats for a user (only chats with messages) - OPTIMIZED"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get("limit", 50, type=int)  # Limit results for speed
        
        # Optimized query: filter in database, not in Python
        # Use inclusion-only projection (MongoDB doesn't allow mixing except _id)
        chats = list(chats_collection.find(
            {
                "userId": user_id,
                "totalMessages": {"$gt": 0}  # Filter in DB for speed
            },
            {
                "_id": 1,
                "chatId": 1,
                "title": 1,
                "createdAt": 1,
                "updatedAt": 1,
                "totalMessages": 1
            }
        ).sort("updatedAt", -1).limit(limit))  # Sort by most recently updated
        
        # Convert ObjectIds and timestamps
        for chat in chats:
            chat["_id"] = str(chat["_id"])
            if "createdAt" in chat and hasattr(chat["createdAt"], 'isoformat'):
                chat["createdAt"] = chat["createdAt"].isoformat()
            if "updatedAt" in chat and hasattr(chat["updatedAt"], 'isoformat'):
                chat["updatedAt"] = chat["updatedAt"].isoformat()
        
        return jsonify({"chats": chats}), 200
    
    except Exception as e:
        logger.error(f"Error listing chats: {str(e)}")
        return jsonify({"error": "Failed to list chats"}), 500


# =======================
# GET RECENT CONVERSATIONS (FROM CURRENT CHAT)
# =======================
@chat_bp.route("/recent", methods=["GET"])
@jwt_required()
def get_recent():
    """Get recent messages from current chat"""
    try:
        user_id = get_jwt_identity()
        chat_id = request.args.get("chatId", None)
        count = request.args.get("count", 10, type=int)
        
        # Get specific chat
        if chat_id:
            chat = chats_collection.find_one({"userId": user_id, "chatId": chat_id})
        else:
            chat = chats_collection.find_one({"userId": user_id}, sort=[("createdAt", -1)])

        if not chat:
            return jsonify({"messages": []}), 200

        messages = chat.get("messages", [])
        
        # Get last N messages
        recent_messages = messages[-count:]
        
        for msg in recent_messages:
            if "timestamp" in msg:
                msg["timestamp"] = msg["timestamp"].isoformat()

        return jsonify({
            "messages": recent_messages,
            "total": len(messages),
            "chatId": chat.get("chatId")
        }), 200

    except Exception as e:
        logger.error(f"Error fetching recent messages: {str(e)}")
        return jsonify({"error": "Failed to fetch recent messages"}), 500


# =======================
# DELETE SINGLE CHAT
# =======================
@chat_bp.route("/delete/<chat_id>", methods=["DELETE"])
@jwt_required()
def delete_chat(chat_id):
    """Delete a single chat"""
    try:
        user_id = get_jwt_identity()

        result = chats_collection.delete_one({"userId": user_id, "chatId": chat_id})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Chat not found"}), 404
        
        logger.info(f"Deleted chat {chat_id} for user {user_id}")
        return jsonify({"message": "Chat deleted"}), 200

    except Exception as e:
        logger.error(f"Error deleting chat: {str(e)}")
        return jsonify({"error": "Failed to delete chat"}), 500


# =======================
# CLEAR ALL CHATS
# =======================
@chat_bp.route("/clear-all", methods=["DELETE"])
@jwt_required()
def clear_all():
    """Delete all chats for a user"""
    try:
        user_id = get_jwt_identity()

        result = chats_collection.delete_many({"userId": user_id})
        
        logger.info(f"Cleared {result.deleted_count} chats for user {user_id}")
        return jsonify({
            "message": "All chats cleared",
            "deletedCount": result.deleted_count
        }), 200
    
    except Exception as e:
        logger.error(f"Error clearing all chats: {str(e)}")
        return jsonify({"error": "Failed to clear chats"}), 500


# =======================
# STREAMING CHAT ENDPOINT (Like ChatGPT/Claude)
# =======================
@chat_bp.route("/stream", methods=["POST"])
@jwt_required()
def stream_chat():
    """Stream chat response in real-time like ChatGPT/Claude using Server-Sent Events"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        question = data.get("question", "").strip()
        chat_id = data.get("chatId", None)

        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Check intent type
        intent = detect_intent(question)
        
        # Handle greetings and non-medical questions without streaming
        if intent != Intent.MEDICAL:
            answer = get_static_response(intent)
            
            # Save to database
            if chat_id:
                chat = chats_collection.find_one({"userId": user_id, "chatId": chat_id})
                if chat:
                    chats_collection.update_one(
                        {"userId": user_id, "chatId": chat_id},
                        {
                            "$push": {"messages": {"$each": [
                                {"role": "user", "content": question, "timestamp": datetime.utcnow()},
                                {"role": "assistant", "content": answer, "timestamp": datetime.utcnow()}
                            ]}},
                            "$set": {"updatedAt": datetime.utcnow()},
                            "$inc": {"totalMessages": 2}
                        }
                    )
            
            return jsonify({
                "answer": answer,
                "chatId": chat_id,
                "intent": intent.value
            }), 200

        # Get or create chat session
        if chat_id:
            chat = chats_collection.find_one({"userId": user_id, "chatId": chat_id})
        else:
            chat = chats_collection.find_one({"userId": user_id}, sort=[("createdAt", -1)])

        if not chat:
            chat_id = str(uuid.uuid4())
            chat_doc = {
                "userId": user_id,
                "chatId": chat_id,
                "messages": [],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                "title": question[:50] + "..." if len(question) > 50 else question,
                "totalMessages": 0
            }
            chats_collection.insert_one(chat_doc)
            chat = chat_doc
        else:
            chat_id = chat["chatId"]
            # Update title if still "New Chat"
            if chat.get("title") == "New Chat":
                chats_collection.update_one(
                    {"userId": user_id, "chatId": chat_id},
                    {"$set": {"title": question[:50] + "..." if len(question) > 50 else question}}
                )

        def generate():
            """Generator for Server-Sent Events"""
            full_response = ""
            try:
                for chunk in stream_medical_answer(question):
                    # Parse the SSE data to extract token
                    if chunk.startswith("data: "):
                        try:
                            data_json = json.loads(chunk[6:])
                            if "token" in data_json:
                                full_response += data_json["token"]
                        except json.JSONDecodeError:
                            pass
                    yield chunk
                
                # After streaming is done, save to database
                if full_response:
                    chats_collection.update_one(
                        {"userId": user_id, "chatId": chat_id},
                        {
                            "$push": {"messages": {"$each": [
                                {"role": "user", "content": question, "timestamp": datetime.utcnow()},
                                {"role": "assistant", "content": full_response, "timestamp": datetime.utcnow()}
                            ]}},
                            "$set": {"updatedAt": datetime.utcnow()},
                            "$inc": {"totalMessages": 2}
                        }
                    )
                    
            except Exception as stream_error:
                logger.error(f"Streaming error: {stream_error}")
                import traceback
                logger.error(traceback.format_exc())
                yield f"data: {json.dumps({'error': str(stream_error)})}\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
                'Access-Control-Allow-Origin': '*'
            }
        )

    except Exception as e:
        logger.error(f"Error in stream endpoint: {str(e)}")
        return jsonify({"error": "Failed to stream response"}), 500


# =======================
# SEARCH CHATS
# =======================
@chat_bp.route("/search", methods=["GET"])
@jwt_required()
def search_chats():
    """Search messages across all chats"""
    try:
        user_id = get_jwt_identity()
        query = request.args.get("q", "").strip()
        
        if not query or len(query) < 2:
            return jsonify({"error": "Search query must be at least 2 characters"}), 400
        
        # Find all chats for user
        chats = list(chats_collection.find({"userId": user_id}))
        
        results = []
        for chat in chats:
            for i, msg in enumerate(chat.get("messages", [])):
                if query.lower() in msg.get("content", "").lower():
                    results.append({
                        "chatId": chat["chatId"],
                        "chatTitle": chat.get("title", "Chat"),
                        "messageIndex": i,
                        "role": msg.get("role"),
                        "content": msg.get("content"),
                        "timestamp": msg.get("timestamp").isoformat() if "timestamp" in msg else None
                    })
        
        return jsonify({
            "query": query,
            "results": results,
            "totalResults": len(results)
        }), 200
    
    except Exception as e:
        logger.error(f"Error searching chats: {str(e)}")
        return jsonify({"error": "Search failed"}), 500


# =======================
# GET CHAT STATS
# =======================
@chat_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    """Get chat statistics for user"""
    try:
        user_id = get_jwt_identity()
        
        # Get all chats
        all_chats = list(chats_collection.find({"userId": user_id}))
        
        total_chats = len(all_chats)
        total_messages = sum(len(chat.get("messages", [])) for chat in all_chats)
        
        # Count exchanges (pairs of messages)
        total_exchanges = total_messages // 2
        
        # Find most recent chat
        most_recent = max(all_chats, key=lambda c: c.get("createdAt", datetime.utcnow())) if all_chats else None
        
        return jsonify({
            "totalChats": total_chats,
            "totalMessages": total_messages,
            "totalExchanges": total_exchanges,
            "recentChatId": most_recent.get("chatId") if most_recent else None,
            "recentChatTime": most_recent.get("createdAt").isoformat() if most_recent and "createdAt" in most_recent else None
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({"error": "Failed to fetch stats"}), 500
