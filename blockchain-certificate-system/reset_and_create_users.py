"""
Reset System and Create Users with Correct Bcrypt Passwords
Run this script to fix the password authentication issue
"""

import os
import json
from models import Student, College, Company
from config import students_col, colleges_col, companies_col, certificates_col, access_logs_col

def clear_database():
    """Clear all existing data"""
    print("\n🗑️  Clearing existing data...")
    try:
        students_col.delete_many({})
        colleges_col.delete_many({})
        companies_col.delete_many({})
        certificates_col.delete_many({})
        access_logs_col.delete_many({})
        print("✓ Database cleared successfully!")
    except Exception as e:
        print(f"✗ Error clearing database: {e}")

def create_directories():
    """Create necessary directories"""
    directories = [
        'NODES/N1', 'NODES/N2', 'NODES/N3', 'NODES/N4',
        'QRcodes', 'templates', 'static'
    ]
    
    print("\n📁 Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ Created: {directory}")

def create_genesis_blocks():
    """Create genesis blocks as proper JSON arrays"""
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
        print(f"  ✓ Created: {filepath}")

def create_users():
    """Create sample users with bcrypt passwords"""
    print("\n👥 Creating users with bcrypt passwords...")
    
    # Create sample college
    print("\n  Creating college...")
    college_id = College.create(
        college_id="ABC001",
        name="ABC Engineering College",
        email="admin@abc.edu",
        phone="9876543210",
        address="123 College Street, City",
        password="college123"
    )
    if college_id:
        print("  ✓ College created successfully")
        print("     College ID: ABC001")
        print("     Password: college123")
    else:
        print("  ✗ Failed to create college")
        return False
    
    # Create sample student
    print("\n  Creating student...")
    student_id = Student.create(
        usn="1ABC21CS001",
        name="John Doe",
        department="Computer Science",
        college_id="ABC001",
        email="john@student.abc.edu",
        phone="9876543211",
        password="student123"
    )
    if student_id:
        print("  ✓ Student created successfully")
        print("     USN: 1ABC21CS001")
        print("     Password: student123")
    else:
        print("  ✗ Failed to create student")
        return False
    
    # Create additional students for testing
    print("\n  Creating additional students...")
    additional_students = [
        {
            "usn": "1ABC21CS002",
            "name": "Jane Smith",
            "department": "Computer Science",
            "college_id": "ABC001",
            "email": "jane@student.abc.edu",
            "phone": "9876543212",
            "password": "student123"
        },
        {
            "usn": "1ABC21EC001",
            "name": "Mike Johnson",
            "department": "Electronics and Communication",
            "college_id": "ABC001",
            "email": "mike@student.abc.edu",
            "phone": "9876543213",
            "password": "student123"
        },
        {
            "usn": "1ABC21ME001",
            "name": "Sarah Williams",
            "department": "Mechanical Engineering",
            "college_id": "ABC001",
            "email": "sarah@student.abc.edu",
            "phone": "9876543214",
            "password": "student123"
        }
    ]
    
    for student_data in additional_students:
        result = Student.create(**student_data)
        if result:
            print(f"  ✓ Created: {student_data['usn']} - {student_data['name']}")
    
    # Create sample company
    print("\n  Creating company...")
    company_id = Company.create(
        company_id="TECH001",
        name="Tech Solutions Pvt Ltd",
        email="hr@techsolutions.com",
        phone="9876543220",
        industry="IT Services",
        password="company123"
    )
    if company_id:
        print("  ✓ Company created successfully")
        print("     Company ID: TECH001")
        print("     Password: company123")
    else:
        print("  ✗ Failed to create company")
        return False
    
    # Create additional company
    company_id2 = Company.create(
        company_id="SOFT002",
        name="Software Innovation Labs",
        email="careers@softlabs.com",
        phone="9876543221",
        industry="Software Development",
        password="company123"
    )
    if company_id2:
        print("  ✓ Created: SOFT002 - Software Innovation Labs")
    
    return True

def verify_credentials():
    """Verify that credentials work"""
    print("\n🔍 Verifying credentials...")
    
    # Test college login
    print("\n  Testing college login...")
    college = College.authenticate("ABC001", "college123")
    if college:
        print(f"  ✓ College login works: {college['Name']}")
    else:
        print("  ✗ College login failed!")
        return False
    
    # Test student login
    print("\n  Testing student login...")
    student = Student.authenticate("1ABC21CS001", "student123")
    if student:
        print(f"  ✓ Student login works: {student['Name']}")
    else:
        print("  ✗ Student login failed!")
        return False
    
    # Test company login
    print("\n  Testing company login...")
    company = Company.authenticate("TECH001", "company123")
    if company:
        print(f"  ✓ Company login works: {company['Name']}")
    else:
        print("  ✗ Company login failed!")
        return False
    
    return True

def main():
    print("=" * 70)
    print("  BLOCKCHAIN CERTIFICATE SYSTEM - RESET & SETUP")
    print("=" * 70)
    
    try:
        # Step 1: Clear database
        clear_database()
        
        # Step 2: Create directories
        create_directories()
        
        # Step 3: Create genesis blocks
        create_genesis_blocks()
        
        # Step 4: Create users
        if not create_users():
            print("\n❌ Failed to create users!")
            return
        
        # Step 5: Verify credentials
        if not verify_credentials():
            print("\n❌ Credential verification failed!")
            return
        
        # Success!
        print("\n" + "=" * 70)
        print("✅ SYSTEM RESET COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        print("\n" + "🔐 LOGIN CREDENTIALS ".center(70, "="))
        print("\n📚 COLLEGE LOGIN:")
        print("   URL: http://127.0.0.1:5000/college/login")
        print("   College ID: ABC001")
        print("   Password: college123")
        
        print("\n👨‍🎓 STUDENT LOGIN:")
        print("   URL: http://127.0.0.1:5000/student/login")
        print("   USN: 1ABC21CS001")
        print("   Password: student123")
        print("\n   Additional Students:")
        print("   - 1ABC21CS002 (Jane Smith) - Computer Science")
        print("   - 1ABC21EC001 (Mike Johnson) - Electronics")
        print("   - 1ABC21ME001 (Sarah Williams) - Mechanical")
        print("   All with password: student123")
        
        print("\n🏢 COMPANY LOGIN:")
        print("   URL: http://127.0.0.1:5000/company/login")
        print("   Company ID: TECH001")
        print("   Password: company123")
        print("\n   Additional Companies:")
        print("   - SOFT002 (Software Innovation Labs)")
        print("   Password: company123")
        
        print("\n" + "=" * 70)
        print("\n📝 NEXT STEPS:")
        print("   1. Run: python main.py")
        print("   2. Open: http://127.0.0.1:5000")
        print("   3. Login with credentials above")
        print("   4. Test the system!")
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()