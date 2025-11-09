"""
FINAL FIX SOLUTION - Direct Database Setup
This script connects to MongoDB and creates users with correct passwords
Run this after MongoDB is started
"""

import bcrypt
from pymongo import MongoClient
import datetime
import json
import os

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "blockchain_certificates"

def test_mongodb_connection():
    """Test if MongoDB is accessible"""
    print("\n" + "="*70)
    print("TESTING MONGODB CONNECTION")
    print("="*70)
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ SUCCESS: MongoDB is running and accessible!")
        print(f"✅ MongoDB Version: {client.server_info()['version']}")
        return True
    except Exception as e:
        print("❌ FAILED: Cannot connect to MongoDB")
        print(f"❌ Error: {e}")
        print("\n💡 SOLUTION:")
        print("   1. Open Command Prompt as Administrator")
        print("   2. Run: net start MongoDB")
        print("   3. Or manually start: mongod --dbpath C:\\data\\db")
        return False

def clear_and_setup():
    """Clear database and create users"""
    
    # Test connection first
    if not test_mongodb_connection():
        return False
    
    print("\n" + "="*70)
    print("SETTING UP DATABASE")
    print("="*70)
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        
        # Get collections
        students_col = db['students']
        colleges_col = db['colleges']
        companies_col = db['companies']
        certificates_col = db['certificates']
        access_logs_col = db['access_logs']
        
        print("\n🗑️  Clearing existing data...")
        students_col.delete_many({})
        colleges_col.delete_many({})
        companies_col.delete_many({})
        certificates_col.delete_many({})
        access_logs_col.delete_many({})
        print("✅ Database cleared!")
        
        # Create College
        print("\n📚 Creating College...")
        college_password = bcrypt.hashpw("college123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        college_data = {
            "CollegeID": "ABC001",
            "Name": "ABC Engineering College",
            "Email": "admin@abc.edu",
            "Phone": "9876543210",
            "Address": "123 College Street, City",
            "Password": college_password,
            "CreatedAt": datetime.datetime.now(),
            "Status": "Active"
        }
        colleges_col.insert_one(college_data)
        print("✅ College created: ABC001")
        print("   Password: college123")
        
        # Create Students
        print("\n👨‍🎓 Creating Students...")
        students_data = [
            {
                "USN": "1ABC21CS001",
                "Name": "John Doe",
                "Department": "Computer Science",
                "CollegeID": "ABC001",
                "Email": "john@student.abc.edu",
                "Phone": "9876543211",
                "Password": bcrypt.hashpw("student123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "CreatedAt": datetime.datetime.now(),
                "Status": "Active"
            },
            {
                "USN": "1ABC21CS002",
                "Name": "Jane Smith",
                "Department": "Computer Science",
                "CollegeID": "ABC001",
                "Email": "jane@student.abc.edu",
                "Phone": "9876543212",
                "Password": bcrypt.hashpw("student123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "CreatedAt": datetime.datetime.now(),
                "Status": "Active"
            },
            {
                "USN": "1ABC21EC001",
                "Name": "Mike Johnson",
                "Department": "Electronics and Communication",
                "CollegeID": "ABC001",
                "Email": "mike@student.abc.edu",
                "Phone": "9876543213",
                "Password": bcrypt.hashpw("student123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "CreatedAt": datetime.datetime.now(),
                "Status": "Active"
            }
        ]
        
        for student in students_data:
            students_col.insert_one(student)
            print(f"✅ Student created: {student['USN']} - {student['Name']}")
        print("   All passwords: student123")
        
        # Create Companies
        print("\n🏢 Creating Companies...")
        companies_data = [
            {
                "CompanyID": "TECH001",
                "Name": "Tech Solutions Pvt Ltd",
                "Email": "hr@techsolutions.com",
                "Phone": "9876543220",
                "Industry": "IT Services",
                "Password": bcrypt.hashpw("company123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "CreatedAt": datetime.datetime.now(),
                "Status": "Active",
                "AccessibleColleges": []
            },
            {
                "CompanyID": "SOFT002",
                "Name": "Software Innovation Labs",
                "Email": "careers@softlabs.com",
                "Phone": "9876543221",
                "Industry": "Software Development",
                "Password": bcrypt.hashpw("company123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "CreatedAt": datetime.datetime.now(),
                "Status": "Active",
                "AccessibleColleges": []
            }
        ]
        
        for company in companies_data:
            companies_col.insert_one(company)
            print(f"✅ Company created: {company['CompanyID']} - {company['Name']}")
        print("   All passwords: company123")
        
        # Create indexes
        print("\n🔧 Creating database indexes...")
        students_col.create_index("USN", unique=True)
        colleges_col.create_index("CollegeID", unique=True)
        companies_col.create_index("CompanyID", unique=True)
        certificates_col.create_index("hash", unique=True)
        print("✅ Indexes created!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_logins():
    """Verify that all logins work"""
    
    print("\n" + "="*70)
    print("VERIFYING LOGINS")
    print("="*70)
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        
        # Test College Login
        print("\n🏛️  Testing College Login...")
        college = db.colleges.find_one({"CollegeID": "ABC001"})
        if college and bcrypt.checkpw("college123".encode('utf-8'), college['Password'].encode('utf-8')):
            print(f"✅ College Login Works: {college['Name']}")
            print("   College ID: ABC001")
            print("   Password: college123")
        else:
            print("❌ College login failed!")
            return False
        
        # Test Student Login
        print("\n👨‍🎓 Testing Student Login...")
        student = db.students.find_one({"USN": "1ABC21CS001"})
        if student and bcrypt.checkpw("student123".encode('utf-8'), student['Password'].encode('utf-8')):
            print(f"✅ Student Login Works: {student['Name']}")
            print("   USN: 1ABC21CS001")
            print("   Password: student123")
        else:
            print("❌ Student login failed!")
            return False
        
        # Test Company Login
        print("\n🏢 Testing Company Login...")
        company = db.companies.find_one({"CompanyID": "TECH001"})
        if company and bcrypt.checkpw("company123".encode('utf-8'), company['Password'].encode('utf-8')):
            print(f"✅ Company Login Works: {company['Name']}")
            print("   Company ID: TECH001")
            print("   Password: company123")
        else:
            print("❌ Company login failed!")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error verifying logins: {e}")
        return False

def create_blockchain_structure():
    """Create blockchain directories and genesis blocks"""
    
    print("\n" + "="*70)
    print("CREATING BLOCKCHAIN STRUCTURE")
    print("="*70)
    
    try:
        # Create directories
        directories = ['NODES/N1', 'NODES/N2', 'NODES/N3', 'NODES/N4', 'QRcodes']
        
        print("\n📁 Creating directories...")
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created: {directory}")
        
        # Create genesis blocks
        genesis = {
            "index": 0,
            "proof": 0,
            "previous_hash": "0",
            "timestamp": "2025-01-01 00:00:00",
            "data": "Genesis Block"
        }
        
        print("\n⛓️  Creating genesis blocks...")
        for i in range(1, 5):
            filepath = f"NODES/N{i}/blockchain.json"
            with open(filepath, 'w') as f:
                json.dump([genesis], f, indent=2)
            print(f"✅ Created: {filepath}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating blockchain structure: {e}")
        return False

def main():
    """Main setup function"""
    
    print("\n" + "="*70)
    print("  🔧 BLOCKCHAIN CERTIFICATE SYSTEM - FINAL FIX  ")
    print("="*70)
    
    print("\n📋 This script will:")
    print("   1. Test MongoDB connection")
    print("   2. Clear old data")
    print("   3. Create users with correct bcrypt passwords")
    print("   4. Create blockchain structure")
    print("   5. Verify all logins work")
    
    input("\n⏸️  Press ENTER to continue or CTRL+C to cancel...")
    
    # Step 1: Setup database
    if not clear_and_setup():
        print("\n❌ FAILED: Could not setup database")
        print("\n💡 Make sure MongoDB is running:")
        print("   net start MongoDB")
        return
    
    # Step 2: Create blockchain structure
    if not create_blockchain_structure():
        print("\n❌ FAILED: Could not create blockchain structure")
        return
    
    # Step 3: Verify logins
    if not verify_logins():
        print("\n❌ FAILED: Login verification failed")
        return
    
    # Success!
    print("\n" + "="*70)
    print("  ✅ SUCCESS! SYSTEM READY TO USE  ")
    print("="*70)
    
    print("\n" + "🔐 LOGIN CREDENTIALS ".center(70, "="))
    
    print("\n📚 COLLEGE LOGIN:")
    print("   URL: http://127.0.0.1:5000/college/login")
    print("   College ID: ABC001")
    print("   Password: college123")
    
    print("\n👨‍🎓 STUDENT LOGIN:")
    print("   URL: http://127.0.0.1:5000/student/login")
    print("   USN: 1ABC21CS001")
    print("   Password: student123")
    print("\n   Other students:")
    print("   - 1ABC21CS002 (Jane Smith)")
    print("   - 1ABC21EC001 (Mike Johnson)")
    print("   All passwords: student123")
    
    print("\n🏢 COMPANY LOGIN:")
    print("   URL: http://127.0.0.1:5000/company/login")
    print("   Company ID: TECH001")
    print("   Password: company123")
    
    print("\n" + "="*70)
    print("\n📝 NEXT STEPS:")
    print("   1. Run: python main.py")
    print("   2. Open: http://127.0.0.1:5000")
    print("   3. Login with credentials above")
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()