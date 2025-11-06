import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# MongoDB Connection Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "blockchain_certificates"

# Collections
CERTIFICATES_COLLECTION = "certificates"
STUDENTS_COLLECTION = "students"
COLLEGES_COLLECTION = "colleges"
COMPANIES_COLLECTION = "companies"
ACCESS_LOGS_COLLECTION = "access_logs"

# Create MongoDB client
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

# Access database
mydb = client[DATABASE_NAME]

# Access collections
certificates_col = mydb[CERTIFICATES_COLLECTION]
students_col = mydb[STUDENTS_COLLECTION]
colleges_col = mydb[COLLEGES_COLLECTION]
companies_col = mydb[COMPANIES_COLLECTION]
access_logs_col = mydb[ACCESS_LOGS_COLLECTION]

# Test connection and create indexes
try:
    client.server_info()
    print("✓ MongoDB connected successfully!")
    
    # Certificate indexes
    certificates_col.create_index("hash", unique=True)
    certificates_col.create_index("USN")
    certificates_col.create_index("Department")
    certificates_col.create_index("CollegeID")
    
    # Student indexes
    students_col.create_index("USN", unique=True)
    students_col.create_index("Department")
    students_col.create_index("CollegeID")
    
    # College indexes
    colleges_col.create_index("CollegeID", unique=True)
    
    # Company indexes
    companies_col.create_index("CompanyID", unique=True)
    
    print("✓ Indexes created successfully!")
    
except ConnectionFailure as e:
    print(f"✗ MongoDB connection failed: {e}")
    print("Please ensure MongoDB is running on localhost:27017")
except Exception as e:
    print(f"✗ Error: {e}")