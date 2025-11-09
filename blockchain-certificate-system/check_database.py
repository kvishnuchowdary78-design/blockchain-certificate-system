"""
Check Database Contents
View all users currently in the database
"""

from config import students_col, colleges_col, companies_col
import bcrypt

def check_colleges():
    """Check all colleges in database"""
    print("\n" + "=" * 70)
    print("🏛️  COLLEGES IN DATABASE")
    print("=" * 70)
    
    colleges = list(colleges_col.find())
    
    if not colleges:
        print("❌ No colleges found!")
        return
    
    for i, college in enumerate(colleges, 1):
        print(f"\n{i}. College ID: {college.get('CollegeID', 'N/A')}")
        print(f"   Name: {college.get('Name', 'N/A')}")
        print(f"   Email: {college.get('Email', 'N/A')}")
        print(f"   Phone: {college.get('Phone', 'N/A')}")
        print(f"   Status: {college.get('Status', 'N/A')}")
        
        # Test password
        test_passwords = ['college123', 'college456', 'password123']
        for pwd in test_passwords:
            try:
                if 'Password' in college and bcrypt.checkpw(pwd.encode('utf-8'), college['Password'].encode('utf-8')):
                    print(f"   ✅ Working Password: {pwd}")
                    break
            except:
                pass

def check_students():
    """Check all students in database"""
    print("\n" + "=" * 70)
    print("👨‍🎓 STUDENTS IN DATABASE")
    print("=" * 70)
    
    students = list(students_col.find())
    
    if not students:
        print("❌ No students found!")
        return
    
    for i, student in enumerate(students, 1):
        print(f"\n{i}. USN: {student.get('USN', 'N/A')}")
        print(f"   Name: {student.get('Name', 'N/A')}")
        print(f"   Department: {student.get('Department', 'N/A')}")
        print(f"   College ID: {student.get('CollegeID', 'N/A')}")
        print(f"   Email: {student.get('Email', 'N/A')}")
        print(f"   Status: {student.get('Status', 'N/A')}")
        
        # Test password
        test_passwords = ['student123', 'password123', 'student456']
        for pwd in test_passwords:
            try:
                if 'Password' in student and bcrypt.checkpw(pwd.encode('utf-8'), student['Password'].encode('utf-8')):
                    print(f"   ✅ Working Password: {pwd}")
                    break
            except:
                pass

def check_companies():
    """Check all companies in database"""
    print("\n" + "=" * 70)
    print("🏢 COMPANIES IN DATABASE")
    print("=" * 70)
    
    companies = list(companies_col.find())
    
    if not companies:
        print("❌ No companies found!")
        return
    
    for i, company in enumerate(companies, 1):
        print(f"\n{i}. Company ID: {company.get('CompanyID', 'N/A')}")
        print(f"   Name: {company.get('Name', 'N/A')}")
        print(f"   Industry: {company.get('Industry', 'N/A')}")
        print(f"   Email: {company.get('Email', 'N/A')}")
        print(f"   Status: {company.get('Status', 'N/A')}")
        
        # Test password
        test_passwords = ['company123', 'password123', 'company456']
        for pwd in test_passwords:
            try:
                if 'Password' in company and bcrypt.checkpw(pwd.encode('utf-8'), company['Password'].encode('utf-8')):
                    print(f"   ✅ Working Password: {pwd}")
                    break
            except:
                pass

def main():
    print("\n" + "🔍 DATABASE CHECKER ".center(70, "="))
    print("Checking what's currently in the database...\n")
    
    try:
        check_colleges()
        check_students()
        check_companies()
        
        print("\n" + "=" * 70)
        print("\n💡 TIP: If passwords don't work, run: python reset_and_create_users.py")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()