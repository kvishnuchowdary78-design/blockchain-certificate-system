"""
System Initialization Script
Creates directories, genesis blocks, and sample users
"""

import os
import json
from models import Student, College, Company

def create_directories():
    """Create necessary directories"""
    directories = [
        'NODES/N1', 'NODES/N2', 'NODES/N3', 'NODES/N4',
        'QRcodes', 'templates', 'static'
    ]
    
    print("Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ Created: {directory}")

def create_genesis_blocks():
    """Create genesis blocks"""
    genesis = {
        "index": 0,
        "proof": 0,
        "previous_hash": "0",
        "timestamp": "2025-01-01 00:00:00",
        "data": "Genesis Block"
    }
    
    print("\nCreating genesis blocks...")
    for i in range(1, 5):
        filepath = f"NODES/N{i}/blockchain.json"
        with open(filepath, 'w') as f:
            json.dump(genesis, f)
        print(f"  ✓ Created: {filepath}")

def create_sample_data():
    """Create sample users"""
    print("\nCreating sample data...")
    
    # Create sample college
    college_id = College.create(
        college_id="ABC001",
        name="ABC Engineering College",
        email="admin@abc.edu",
        phone="9876543210",
        address="123 College Street, City",
        password="college123"
    )
    if college_id:
        print("  ✓ Sample college created (ID: ABC001, Password: college123)")
    
    # Create sample student
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
        print("  ✓ Sample student created (USN: 1ABC21CS001, Password: student123)")
    
    # Create sample company
    company_id = Company.create(
        company_id="TECH001",
        name="Tech Solutions Pvt Ltd",
        email="hr@techsolutions.com",
        phone="9876543212",
        industry="IT Services",
        password="company123"
    )
    if company_id:
        print("  ✓ Sample company created (ID: TECH001, Password: company123)")

def main():
    print("=" * 70)
    print("  System Initialization")
    print("=" * 70)
    
    try:
        create_directories()
        create_genesis_blocks()
        create_sample_data()
        
        print("\n" + "=" * 70)
        print("✅ System initialized successfully!")
        print("=" * 70)
        print("\n📝 Sample Login Credentials:")
        print("\nCollege Login:")
        print("  College ID: ABC001")
        print("  Password: college123")
        print("\nStudent Login:")
        print("  USN: 1ABC21CS001")
        print("  Password: student123")
        print("\nCompany Login:")
        print("  Company ID: TECH001")
        print("  Password: company123")
        print("\n🚀 Run: python main.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()