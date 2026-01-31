from extensions.db import db

# Store individual chats (one per conversation session)
chats_collection = db.chats

# Each chat document structure:
# {
#   "_id": ObjectId,
#   "userId": "user_id",
#   "chatId": "unique_chat_id",
#   "messages": [
#       {"role": "user", "content": "...", "timestamp": datetime},
#       {"role": "assistant", "content": "...", "timestamp": datetime}
#   ],
#   "createdAt": datetime,
#   "updatedAt": datetime,
#   "title": "Chat title (first message summary)",
#   "totalMessages": 0
# }
