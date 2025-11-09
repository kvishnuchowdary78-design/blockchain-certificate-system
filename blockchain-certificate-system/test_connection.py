from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
    client.server_info()
    print("✅ MongoDB IS RUNNING!")
    print(f"Version: {client.server_info()['version']}")
except:
    print("❌ MongoDB IS NOT RUNNING!")
    print("\nSOLUTION:")
    print("1. Double-click: start_mongodb.bat")
    print("2. Or run as admin: net start MongoDB")