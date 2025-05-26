from pymongo import MongoClient

MONGO_URI = "mongodb+srv://chatbot_user:chatbot123@chatbotcluster.rw94opl.mongodb.net/?retryWrites=true&w=majority&appName=ChatbotCluster"
client = MongoClient(MONGO_URI)

try:
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print("❌ Failed to connect:", e)

