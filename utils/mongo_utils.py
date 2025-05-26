import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "chat_db"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
chats_collection = db["chat_history"]


def store_chat(user_id, session_id, query, response):
    """
    Store a chat interaction in MongoDB.
    
    Args:
        user_id (str): ID of the user
        session_id (str): ID of the session
        query (str): The user's query
        response (str): The assistant's response
    """
    chat_record = {
        "user_id": user_id,
        "session_id": session_id,
        "query": query,
        "response": response,
        "timestamp": datetime.utcnow()
    }
    chats_collection.insert_one(chat_record)


def fetch_chat_history(user_id: str, session_id: str, limit: int = 5) -> str:
    """
    Fetch the last `limit` chat interactions for a specific user and session.
    
    Args:
        user_id (str): Unique user ID
        session_id (str): Unique session ID
        limit (int): Number of recent messages to fetch

    Returns:
        str: A formatted string of chat history
    """
    records = (
        chats_collection.find({"user_id": user_id, "session_id": session_id})
        .sort("timestamp", -1)
        .limit(limit)
    )
    history = [
        f"User: {record['query']}\nAssistant: {record['response']}"
        for record in reversed(list(records))
    ]
    return "\n\n".join(history)


def clear_chat(user_id, session_id):
    """
    Clears the chat history for a specific user and session.
    
    Args:
        user_id (str): ID of the user
        session_id (str): ID of the session
    """
    try:
        chats_collection.delete_many({"user_id": user_id, "session_id": session_id})
    except Exception as e:
        print(f"Error clearing chat: {e}")
