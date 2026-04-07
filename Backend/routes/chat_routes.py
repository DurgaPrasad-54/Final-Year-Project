from flask import Blueprint, request, jsonify, Response, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from models.chat_model import chats_collection
from services.medchat_gemini import (
    detect_intent,
    handle_question,
    stream_medical_answer,
    get_static_response,
    Intent,
)
from services.emotion_detection import (
    detect_emotion,
    get_emotion_emoji,
    is_strong_emotion,
    get_empathetic_response,
)
from datetime import datetime, timezone
import logging
import json
import uuid

logger = logging.getLogger(__name__)
chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


# =======================
# HELPER: Convert string to ObjectId safely
# =======================
def to_object_id(user_id_str):
    """Convert string user ID to ObjectId"""
    try:
        if isinstance(user_id_str, ObjectId):
            return user_id_str
        return ObjectId(user_id_str)
    except Exception as e:
        logger.error(f"Invalid ObjectId: {user_id_str}, error: {e}")
        return None


# =======================
# SESSION MANAGEMENT HELPERS
# =======================
def initialize_session_history():
    """Initialize session history on first chat"""
    try:
        if "history" not in session:
            session["history"] = []
            session.modified = True
            logger.debug("Initialized session history")
    except Exception as e:
        logger.warning(f"Failed to initialize session history: {e}")
        # Continue without session history if it fails


def add_to_session_history(message):
    """Add message to session history (keep last 20)"""
    try:
        if "history" not in session:
            session["history"] = []
        
        if not isinstance(message, dict):
            logger.warning(f"Invalid message type for session history: {type(message)}")
            return
        
        session["history"].append(message)
        
        # Keep only last 20 messages
        if len(session["history"]) > 20:
            session["history"] = session["history"][-20:]
        
        session.modified = True
        logger.debug(f"Session history updated, total messages: {len(session['history'])}")
    except Exception as e:
        logger.warning(f"Failed to add message to session history: {e}")


def get_session_history_count():
    """Get the current message count in session"""
    try:
        return len(session.get("history", []))
    except Exception as e:
        logger.warning(f"Failed to get session history count: {e}")
        return 0


def clear_session_history():
    """Clear all session history"""
    try:
        session["history"] = []
        session.modified = True
        logger.debug("Session history cleared")
    except Exception as e:
        logger.warning(f"Failed to clear session history: {e}")


# =======================
# CREATE NEW CHAT
# =======================

@chat_bp.route("/new", methods=["POST"])
@jwt_required()
def new_chat():
    """Create a new chat session with 0 messages"""
    try:
        user_id_str = get_jwt_identity()
        user_id = to_object_id(user_id_str)
        
        if not user_id:
            return jsonify({"error": "Invalid user ID"}), 400
        
        chat_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Initialize session history
        initialize_session_history()
        
        chat_doc = {
            "userId": user_id_str,  # Store as string for easier querying
            "chatId": chat_id,
            "messages": [],
            "createdAt": now,
            "updatedAt": now,
            "title": "New Chat",
            "totalMessages": 0
        }
        
        # Insert into database
        result = chats_collection.insert_one(chat_doc)
        logger.info(f"[OK] Created new chat {chat_id} for user {user_id_str} with 0 messages")
        
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
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to create chat"}), 500


# =======================
# ASK QUESTION
# =======================
@chat_bp.route("/ask", methods=["POST"])
@jwt_required()
def ask():
    """Ask a question - handles medical questions AND greetings"""
    try:
        user_id_str = get_jwt_identity()
        data = request.get_json() or {}
        question = data.get("question", "").strip()
        chat_id = data.get("chatId", None)

        if not question:
            return jsonify({"error": "Question is required"}), 400

        if len(question) < 2:
            return jsonify({"error": "Question must be at least 2 characters"}), 400

        logger.info(f"[ASK] User: {user_id_str}, Chat: {chat_id}, Question: {question[:50]}")

        # 1️⃣ Detect intent using new service
        intent = detect_intent(question)
        question_type = intent.value
        
        # 1️⃣.5️⃣ Detect emotion from user input
        emotion, confidence = detect_emotion(question)
        emotion_emoji = get_emotion_emoji(emotion)
        
        # 2️⃣ Get or create chat session
        chat = None
        is_first_message = False
        
        if chat_id:
            # Find existing chat by chatId and userId (as string)
            chat = chats_collection.find_one({"userId": user_id_str, "chatId": chat_id})
            logger.info(f"[LOOKUP] Found existing chat: {chat is not None}")
        else:
            # Get most recent chat
            chat = chats_collection.find_one(
                {"userId": user_id_str}, 
                sort=[("createdAt", -1)]
            )
            logger.info(f"[LOOKUP] Found recent chat: {chat is not None}")

        if not chat:
            # Create new chat with question as title
            chat_id = str(uuid.uuid4())
            chat_title = question[:50] + "..." if len(question) > 50 else question
            now = datetime.now(timezone.utc)
            chat_doc = {
                "userId": user_id_str,  # Store as string
                "chatId": chat_id,
                "messages": [],  # Empty array
                "createdAt": now,
                "updatedAt": now,
                "title": chat_title,
                "totalMessages": 0,
                "lastEmotion": emotion.value,
                "lastEmotionEmoji": emotion_emoji
            }
            result = chats_collection.insert_one(chat_doc)
            chat = chat_doc
            is_first_message = True
            logger.info(f"[CREATE] New chat created: {chat_id}, inserted_id: {result.inserted_id}")
        else:
            chat_id = chat["chatId"]
            is_first_message = chat.get("totalMessages", 0) == 0
            # Update title if it's still "New Chat" and this is first real message
            if chat.get("title") == "New Chat" and is_first_message:
                new_title = question[:50] + "..." if len(question) > 50 else question
                chats_collection.update_one(
                    {"userId": user_id_str, "chatId": chat_id},
                    {"$set": {"title": new_title}}
                )
                logger.info(f"[UPDATE] Updated chat title: {new_title[:30]}")

        # 3️⃣ Generate response based on intent
        if intent != Intent.MEDICAL:
            # Handle non-medical intents (greeting, thanks, goodbye, identity, reject)
            answer = get_static_response(intent)
            context_used = False
        else:
            # Medical question - use Groq LLM
            # Validate history before using
            history = chat.get("messages", [])
            if not isinstance(history, list):
                logger.warning(f"Invalid history type: {type(history)}, resetting to empty list")
                history = []
            history = history[-3:]  # Last 3 messages for context
            
            try:
                answer = handle_question(question, history=history)
            except Exception as e:
                logger.error(f"Error generating answer: {e}")
                answer = "I encountered an error processing your question. Please try again."
            
            context_used = True
            
            # Validate response
            if not answer or not isinstance(answer, str) or len(answer.strip()) < 5:
                answer = "I understand you're asking about a health topic. Could you please provide more details or rephrase your question? I'm here to help with medical information."

        # 3️⃣.5️⃣ Prepend empathetic response if strong emotion detected on first message
        if is_first_message and is_strong_emotion(emotion, confidence):
            empathetic = get_empathetic_response(emotion)
            answer = empathetic + answer

        # Initialize session history
        initialize_session_history()
        
        # 4️⃣ Store messages in database with emotion data
        now = datetime.now(timezone.utc)
        user_msg = {
            "role": "user",
            "content": question,
            "timestamp": now,
            "emotion": emotion.value,
            "emotionEmoji": emotion_emoji,
            "emotionConfidence": confidence
        }
        assistant_msg = {
            "role": "assistant",
            "content": answer,
            "timestamp": now,
            "contextUsed": context_used
        }
        
        # *** CRITICAL FIX: Use userId as string, not ObjectId ***
        update_result = chats_collection.update_one(
            {"userId": user_id_str, "chatId": chat_id},  # Match criteria
            {
                "$push": {"messages": {"$each": [user_msg, assistant_msg]}},
                "$set": {
                    "updatedAt": datetime.now(timezone.utc),
                    "lastEmotion": emotion.value,
                    "lastEmotionEmoji": emotion_emoji
                },
                "$inc": {"totalMessages": 2}
            }
        )
        
        # Log the update result
        logger.info(f"[DB UPDATE] Matched: {update_result.matched_count}, Modified: {update_result.modified_count}")
        
        if update_result.matched_count == 0:
            logger.error(f"[DB ERROR] No chat found with userId={user_id_str}, chatId={chat_id}")
            return jsonify({"error": "Chat not found for update"}), 404
        
        if update_result.modified_count == 0:
            logger.warning(f"[DB WARNING] Chat matched but not modified")
        
        # Verify the messages were actually saved
        updated_chat = chats_collection.find_one({"userId": user_id_str, "chatId": chat_id})
        if updated_chat:
            actual_message_count = len(updated_chat.get("messages", []))
            logger.info(f"[VERIFY] Chat {chat_id} now has {actual_message_count} messages in DB")
        else:
            logger.error(f"[VERIFY] Could not find chat {chat_id} after update!")
        
        # Add to session history
        add_to_session_history({"role": "user", "content": question, "emotion": emotion.value, "emotionEmoji": emotion_emoji})
        add_to_session_history({"role": "assistant", "content": answer})
        
        history_count = get_session_history_count()
        logger.info(f"[OK] Response generated for chat {chat_id} (type: {question_type}, emotion: {emotion.value}, session_history: {history_count})")

        return jsonify({
            "answer": answer,
            "chatId": chat_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contextUsed": context_used,
            "questionType": question_type,
            "emotion": emotion.value,
            "emotionEmoji": emotion_emoji,
            "emotionConfidence": confidence,
            "history_count": history_count
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
        user_id_str = get_jwt_identity()
        chat_id = request.args.get("chatId", None)
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 50, type=int)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 50
        
        # Get specific chat - use string userId
        if chat_id:
            chat = chats_collection.find_one({"userId": user_id_str, "chatId": chat_id})
        else:
            # Get most recent chat
            chat = chats_collection.find_one({"userId": user_id_str}, sort=[("createdAt", -1)])
        
        if not chat:
            return jsonify({"error": "Chat not found"}), 404
        
        # Get all messages from this chat
        messages = chat.get("messages", [])
        total_messages = len(messages)
        
        logger.info(f"[HISTORY] Chat {chat.get('chatId')} has {total_messages} messages")
        
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
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to fetch history"}), 500


# =======================
# GET ALL CHATS (SUMMARY)
# =======================
@chat_bp.route("/list", methods=["GET"])
@jwt_required()
def list_chats():
    """Get list of all chats for a user (only chats with messages) - OPTIMIZED"""
    try:
        user_id_str = get_jwt_identity()
        limit = request.args.get("limit", 50, type=int)        
        # Validate limit parameter
        if limit < 1 or limit > 100:
            limit = 50        
        # Optimized query: filter in database, not in Python
        # Use string userId for consistency
        chats = list(chats_collection.find(
            {
                "userId": user_id_str,
                "totalMessages": {"$gt": 0}  # Filter in DB for speed
            },
            {
                "_id": 1,
                "chatId": 1,
                "title": 1,
                "createdAt": 1,
                "updatedAt": 1,
                "totalMessages": 1,
                "lastEmotion": 1,
                "lastEmotionEmoji": 1
            }
        ).sort("updatedAt", -1).limit(limit))  # Sort by most recently updated
        
        logger.info(f"[LIST] Found {len(chats)} chats for user {user_id_str}")
        
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
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to list chats"}), 500


# =======================
# GET RECENT CONVERSATIONS (FROM CURRENT CHAT)
# =======================
@chat_bp.route("/recent", methods=["GET"])
@jwt_required()
def get_recent():
    """Get recent messages from current chat"""
    try:
        user_id_str = get_jwt_identity()
        chat_id = request.args.get("chatId", None)
        count = request.args.get("count", 10, type=int)
        
        # Get specific chat - use string userId
        if chat_id:
            chat = chats_collection.find_one({"userId": user_id_str, "chatId": chat_id})
        else:
            chat = chats_collection.find_one({"userId": user_id_str}, sort=[("createdAt", -1)])

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
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to fetch recent messages"}), 500


# =======================
# DELETE SINGLE CHAT
# =======================
@chat_bp.route("/delete/<chat_id>", methods=["DELETE"])
@jwt_required()
def delete_chat(chat_id):
    """Delete a single chat"""
    try:
        user_id_str = get_jwt_identity()

        result = chats_collection.delete_one({"userId": user_id_str, "chatId": chat_id})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Chat not found"}), 404
        
        logger.info(f"Deleted chat {chat_id} for user {user_id_str}")
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
        user_id_str = get_jwt_identity()

        result = chats_collection.delete_many({"userId": user_id_str})
        
        logger.info(f"Cleared {result.deleted_count} chats for user {user_id_str}")
        return jsonify({
            "message": "All chats cleared",
            "deletedCount": result.deleted_count
        }), 200
    
    except Exception as e:
        logger.error(f"Error clearing all chats: {str(e)}")
        return jsonify({"error": "Failed to clear chats"}), 500


# =======================
# CLEAR SESSION HISTORY
# =======================
@chat_bp.route("/clear", methods=["POST"])
@jwt_required()
def clear_session():
    """Clear session conversation history (last 20 messages)"""
    try:
        user_id_str = get_jwt_identity()
        clear_session_history()
        
        logger.info(f"Cleared session history for user {user_id_str}")
        return jsonify({
            "message": "Session history cleared",
            "history_count": 0
        }), 200
    
    except Exception as e:
        logger.error(f"Error clearing session history: {str(e)}")
        return jsonify({"error": "Failed to clear session history"}), 500


# =======================
# STREAMING CHAT ENDPOINT (Like ChatGPT/Claude)
# =======================
@chat_bp.route("/stream", methods=["POST"])
@jwt_required()
def stream_chat():
    """Stream chat response in real-time like ChatGPT/Claude using Server-Sent Events"""
    try:
        user_id_str = get_jwt_identity()
        data = request.get_json() or {}
        question = data.get("question", "").strip()
        chat_id = data.get("chatId", None)

        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Detect emotion
        emotion, confidence = detect_emotion(question)
        emotion_emoji = get_emotion_emoji(emotion)

        # Check intent type
        intent = detect_intent(question)
        
        # Handle greetings and non-medical questions without streaming
        if intent != Intent.MEDICAL:
            answer = get_static_response(intent)
            
            # Initialize session history
            initialize_session_history()
            
            # Save to database
            if chat_id:
                chat = chats_collection.find_one({"userId": user_id_str, "chatId": chat_id})
                if chat:
                    now = datetime.now(timezone.utc)
                    chats_collection.update_one(
                        {"userId": user_id_str, "chatId": chat_id},
                        {
                            "$push": {"messages": {"$each": [
                                {
                                    "role": "user",
                                    "content": question,
                                    "timestamp": now,
                                    "emotion": emotion.value,
                                    "emotionEmoji": emotion_emoji,
                                    "emotionConfidence": confidence
                                },
                                {"role": "assistant", "content": answer, "timestamp": now}
                            ]}},
                            "$set": {
                                "updatedAt": now,
                                "lastEmotion": emotion.value,
                                "lastEmotionEmoji": emotion_emoji
                            },
                            "$inc": {"totalMessages": 2}
                        }
                    )
            
            # Add to session history
            add_to_session_history({"role": "user", "content": question, "emotion": emotion.value, "emotionEmoji": emotion_emoji})
            add_to_session_history({"role": "assistant", "content": answer})
            history_count = get_session_history_count()
            
            return jsonify({
                "answer": answer,
                "chatId": chat_id,
                "intent": intent.value,
                "emotion": emotion.value,
                "emotionEmoji": emotion_emoji,
                "emotionConfidence": confidence,
                "history_count": history_count
            }), 200

        # Get or create chat session - use string userId
        if chat_id:
            chat = chats_collection.find_one({"userId": user_id_str, "chatId": chat_id})
        else:
            chat = chats_collection.find_one({"userId": user_id_str}, sort=[("createdAt", -1)])

        if not chat:
            chat_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            chat_doc = {
                "userId": user_id_str,  # String userId
                "chatId": chat_id,
                "messages": [],
                "createdAt": now,
                "updatedAt": now,
                "title": question[:50] + "..." if len(question) > 50 else question,
                "totalMessages": 0,
                "lastEmotion": emotion.value,
                "lastEmotionEmoji": emotion_emoji
            }
            chats_collection.insert_one(chat_doc)
            chat = chat_doc
            is_first_message = True
        else:
            chat_id = chat["chatId"]
            is_first_message = chat.get("totalMessages", 0) == 0
            # Update title if still "New Chat"
            if chat.get("title") == "New Chat":
                chats_collection.update_one(
                    {"userId": user_id_str, "chatId": chat_id},
                    {"$set": {"title": question[:50] + "..." if len(question) > 50 else question}}
                )

        def generate():
            """Generator for Server-Sent Events"""
            full_response = ""
            try:
                # Prepend empathetic response if strong emotion on first message
                if is_first_message and is_strong_emotion(emotion, confidence):
                    empathetic = get_empathetic_response(emotion)
                    full_response = empathetic
                    # Yield the empathetic part first
                    yield f"data: {json.dumps({'token': empathetic})}\n\n"
                
                try:
                    stream_generator = stream_medical_answer(question)
                    if stream_generator is None:
                        raise RuntimeError("stream_medical_answer returned None")
                    
                    for chunk in stream_generator:
                        # Validate chunk is string
                        if not isinstance(chunk, str):
                            logger.warning(f"Invalid chunk type: {type(chunk)}")
                            continue
                        
                        # Parse the SSE data to extract token
                        if chunk.startswith("data: "):
                            try:
                                data_json = json.loads(chunk[6:])
                                if "token" in data_json:
                                    full_response += str(data_json["token"])
                            except json.JSONDecodeError as parse_error:
                                logger.debug(f"Failed to parse chunk: {parse_error}")
                                pass
                        yield chunk
                except Exception as stream_error:
                    logger.error(f"Streaming failed: {stream_error}")
                    error_msg = f"data: {json.dumps({'error': 'Stream processing failed', 'details': str(stream_error)})}\n\n"
                    yield error_msg
                    full_response = full_response or "I encountered an error while generating your response. Please try again."
                    return
                
                # After streaming is done, save to database
                if full_response and isinstance(full_response, str) and len(full_response.strip()) > 0:
                    # Initialize session history
                    initialize_session_history()
                    
                    # Use string userId
                    try:
                        now = datetime.now(timezone.utc)
                        update_result = chats_collection.update_one(
                            {"userId": user_id_str, "chatId": chat_id},
                            {
                                "$push": {"messages": {"$each": [
                                    {
                                        "role": "user",
                                        "content": question,
                                        "timestamp": now,
                                        "emotion": emotion.value,
                                        "emotionEmoji": emotion_emoji,
                                        "emotionConfidence": confidence
                                    },
                                    {"role": "assistant", "content": full_response, "timestamp": now}
                                ]}},
                                "$set": {
                                    "updatedAt": now,
                                    "lastEmotion": emotion.value,
                                    "lastEmotionEmoji": emotion_emoji
                                },
                                "$inc": {"totalMessages": 2}
                            }
                        )
                        if update_result.matched_count == 0:
                            logger.error(f"Chat not found for saving stream: {chat_id}")
                    except Exception as db_error:
                        logger.error(f"Failed to save streamed response to database: {db_error}")
                    
                    # Add to session history
                    add_to_session_history({"role": "user", "content": question, "emotion": emotion.value, "emotionEmoji": emotion_emoji})
                    add_to_session_history({"role": "assistant", "content": full_response})
                    
            except Exception as stream_error:
                logger.error(f"Critical streaming error: {stream_error}")
                import traceback
                logger.error(traceback.format_exc())
                yield f"data: {json.dumps({'error': 'Critical streaming error', 'details': str(stream_error)})}\n\n"

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
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to stream response"}), 500


# =======================
# SEARCH CHATS
# =======================
@chat_bp.route("/search", methods=["GET"])
@jwt_required()
def search_chats():
    """Search messages across all chats"""
    try:
        user_id_str = get_jwt_identity()
        query = request.args.get("q", "").strip()
        
        if not query or len(query) < 2:
            return jsonify({"error": "Search query must be at least 2 characters"}), 400
        
        # Find all chats for user - use string userId
        chats = list(chats_collection.find({"userId": user_id_str}))
        
        results = []
        for chat in chats:
            for i, msg in enumerate(chat.get("messages", [])):
                if query.lower() in msg.get("content", "").lower():
                    timestamp_str = None
                    if "timestamp" in msg and hasattr(msg["timestamp"], 'isoformat'):
                        try:
                            timestamp_str = msg["timestamp"].isoformat()
                        except Exception as e:
                            logger.warning(f"Failed to convert timestamp: {e}")
                    
                    results.append({
                        "chatId": chat["chatId"],
                        "chatTitle": chat.get("title", "Chat"),
                        "messageIndex": i,
                        "role": msg.get("role"),
                        "content": msg.get("content"),
                        "timestamp": timestamp_str
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
        user_id_str = get_jwt_identity()
        
        # Get all chats - use string userId
        all_chats = list(chats_collection.find({"userId": user_id_str}))
        
        total_chats = len(all_chats)
        total_messages = sum(len(chat.get("messages", [])) for chat in all_chats)
        
        # Count exchanges (pairs of messages)
        total_exchanges = total_messages // 2
        
        # Find most recent chat
        most_recent = max(all_chats, key=lambda c: c.get("createdAt", datetime.now(timezone.utc))) if all_chats else None
        
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