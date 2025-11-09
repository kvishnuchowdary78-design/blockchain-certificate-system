"""
SETUP ONCE - Smart Setup Script
Only creates users if they don't exist
Will NOT delete your existing data
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
        return False

def check_existing_data():
    """Check if data already exists"""
    print("\n" + "="*70)
    print("CHECKING EXISTING DATA")
    print("="*70)
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        
        colleges_count = db.colleges.count_documents({})
        students_count = db.students.count_documents({})
        companies_count = db.companies.count_documents({})
        certificates_count = db.certificates.count_documents({})
        
        print(f"\nCurrent Database Status:")
        print(f"  Colleges: {colleges_count}")
        print(f"  Students: {students_count}")
        print(f"  Companies: {companies_count}")
        print(f"  Certificates: {certificates_count}")
        
        if colleges_count > 0 or students_count > 0 or companies_count > 0:
            print("\n⚠️  DATA ALREADY EXISTS!")
            print("   This script will NOT delete existing data.")
            print("   It will only add missing default users if needed.")
            return True
        else:
            print("\n✓ Database is empty. Will create initial data.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error checking data: {e}")
        return False

def setup_users():
    """Setup users only if they don't exist"""
    
    if not test_mongodb_connection():
        return False
    
    data_exists = check_existing_data()
    
    print("\n" + "="*70)
    print("SETTING UP USERS")
    print("="*70)
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        
        # Get collections
        students_col = db['students']
        colleges_col = db['colleges']
        companies_col = db['companies']
        
        # Create College if doesn't exist
        print("\n📚 Checking College...")
        if colleges_col.find_one({"CollegeID": "ABC001"}):
            print("✓ College ABC001 already exists")
        else:
            print("  Creating College ABC001...")
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
        
        # Create Students if don't exist
        print("\n👨‍🎓 Checking Students...")
        students_to_create = [
            {
                "USN": "1ABC21CS001",
                "Name": "John Doe",
                "Department": "Computer Science",
                "CollegeID": "ABC001",
                "Email": "john@student.abc.edu",
                "Phone": "9876543211",
            },
            {
                "USN": "1ABC21CS002",
                "Name": "Jane Smith",
                "Department": "Computer Science",
                "CollegeID": "ABC001",
                "Email": "jane@student.abc.edu",
                "Phone": "9876543212",
            },
            {
                "USN": "1ABC21EC001",
                "Name": "Mike Johnson",
                "Department": "Electronics and Communication",
                "CollegeID": "ABC001",
                "Email": "mike@student.abc.edu",
                "Phone": "9876543213",
            }
        ]
        
        for student_info in students_to_create:
            if students_col.find_one({"USN": student_info["USN"]}):
                print(f"✓ Student {student_info['USN']} already exists")
            else:
                student_info["Password"] = bcrypt.hashpw("student123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                student_info["CreatedAt"] = datetime.datetime.now()
                student_info["Status"] = "Active"
                students_col.insert_one(student_info)
                print(f"✅ Student created: {student_info['USN']} - {student_info['Name']}")
        
        print("   All student passwords: student123")
        
        # Create Companies if don't exist
        print("\n🏢 Checking Companies...")
        companies_to_create = [
            {
                "CompanyID": "TECH001",
                "Name": "Tech Solutions Pvt Ltd",
                "Email": "hr@techsolutions.com",
                "Phone": "9876543220",
                "Industry": "IT Services",
            },
            {
                "CompanyID": "SOFT002",
                "Name": "Software Innovation Labs",
                "Email": "careers@softlabs.com",
                "Phone": "9876543221",
                "Industry": "Software Development",
            }
        ]
        
        for company_info in companies_to_create:
            if companies_col.find_one({"CompanyID": company_info["CompanyID"]}):
                print(f"✓ Company {company_info['CompanyID']} already exists")
            else:
                company_info["Password"] = bcrypt.hashpw("company123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                company_info["CreatedAt"] = datetime.datetime.now()
                company_info["Status"] = "Active"
                company_info["AccessibleColleges"] = []
                companies_col.insert_one(company_info)
                print(f"✅ Company created: {company_info['CompanyID']} - {company_info['Name']}")
        
        print("   All company passwords: company123")
        
        # Create indexes (safe to run multiple times)
        print("\n🔧 Creating/verifying database indexes...")
        students_col.create_index("USN", unique=True)
        colleges_col.create_index("CollegeID", unique=True)
        companies_col.create_index("CompanyID", unique=True)
        db.certificates.create_index("hash", unique=True)
        print("✅ Indexes verified!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up users: {e}")
        import traceback
        traceback.print_exc()
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
            if os.path.exists(directory):
                print(f"✓ {directory} already exists")
            else:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created: {directory}")
        
        # Create genesis blocks only if they don't exist
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
            if os.path.exists(filepath):
                print(f"✓ {filepath} already exists")
            else:
                with open(filepath, 'w') as f:
                    json.dump([genesis], f, indent=2)
                print(f"✅ Created: {filepath}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating blockchain structure: {e}")
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
        else:
            print("❌ College login failed!")
            return False
        
        # Test Student Login
        print("\n👨‍🎓 Testing Student Login...")
        student = db.students.find_one({"USN": "1ABC21CS001"})
        if student and bcrypt.checkpw("student123".encode('utf-8'), student['Password'].encode('utf-8')):
            print(f"✅ Student Login Works: {student['Name']}")
        else:
            print("❌ Student login failed!")
            return False
        
        # Test Company Login
        print("\n🏢 Testing Company Login...")
        company = db.companies.find_one({"CompanyID": "TECH001"})
        if company and bcrypt.checkpw("company123".encode('utf-8'), company['Password'].encode('utf-8')):
            print(f"✅ Company Login Works: {company['Name']}")
        else:
            print("❌ Company login failed!")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error verifying logins: {e}")
        return False

def main():
    """Main setup function"""
    
    print("\n" + "="*70)
    print("  🔧 SMART SETUP - NO DATA LOSS  ")
    print("="*70)
    
    print("\n📋 This script will:")
    print("   ✅ Check if MongoDB is running")
    print("   ✅ Check existing data (will NOT delete)")
    print("   ✅ Create missing users only")
    print("   ✅ Create blockchain structure if needed")
    print("   ✅ Verify all logins work")
    print("\n   ⚠️  YOUR EXISTING DATA WILL NOT BE DELETED!")
    
    input("\n⏸️  Press ENTER to continue or CTRL+C to cancel...")
    
    # Step 1: Setup users (smart - won't delete existing)
    if not setup_users():
        print("\n❌ FAILED: Could not setup users")
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
    print("\n💡 TIP: You can run this script again anytime.")
    print("   It will NOT delete your data!")
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