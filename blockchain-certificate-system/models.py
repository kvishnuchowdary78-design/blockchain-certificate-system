from config import students_col, colleges_col, companies_col, certificates_col, access_logs_col
import hashlib
import datetime

class Student:
    @staticmethod
    def create(usn, name, department, college_id, email, phone, password):
        """Create new student"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        student = {
            "USN": usn.upper(),
            "Name": name,
            "Department": department,
            "CollegeID": college_id,
            "Email": email,
            "Phone": phone,
            "Password": password_hash,
            "CreatedAt": datetime.datetime.now(),
            "Status": "Active"
        }
        
        try:
            result = students_col.insert_one(student)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating student: {e}")
            return None
    
    @staticmethod
    def authenticate(usn, password):
        """Authenticate student"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        student = students_col.find_one({
            "USN": usn.upper(),
            "Password": password_hash,
            "Status": "Active"
        })
        return student
    
    @staticmethod
    def get_by_usn(usn):
        """Get student by USN"""
        return students_col.find_one({"USN": usn.upper()})
    
    @staticmethod
    def get_certificates(usn):
        """Get all certificates for a student"""
        return list(certificates_col.find({"USN": usn.upper()}))


class College:
    @staticmethod
    def create(college_id, name, email, phone, address, password):
        """Create new college"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        college = {
            "CollegeID": college_id.upper(),
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Address": address,
            "Password": password_hash,
            "CreatedAt": datetime.datetime.now(),
            "Status": "Active"
        }
        
        try:
            result = colleges_col.insert_one(college)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating college: {e}")
            return None
    
    @staticmethod
    def authenticate(college_id, password):
        """Authenticate college"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        college = colleges_col.find_one({
            "CollegeID": college_id.upper(),
            "Password": password_hash,
            "Status": "Active"
        })
        return college
    
    @staticmethod
    def get_students(college_id, department=None):
        """Get all students of a college"""
        query = {"CollegeID": college_id.upper()}
        if department:
            query["Department"] = department
        return list(students_col.find(query))
    
    @staticmethod
    def get_certificates(college_id, department=None):
        """Get all certificates of a college"""
        query = {"CollegeID": college_id.upper()}
        if department:
            query["Department"] = department
        return list(certificates_col.find(query))


class Company:
    @staticmethod
    def create(company_id, name, email, phone, industry, password):
        """Create new company"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        company = {
            "CompanyID": company_id.upper(),
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Industry": industry,
            "Password": password_hash,
            "CreatedAt": datetime.datetime.now(),
            "Status": "Active",
            "AccessibleColleges": []
        }
        
        try:
            result = companies_col.insert_one(company)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating company: {e}")
            return None
    
    @staticmethod
    def authenticate(company_id, password):
        """Authenticate company"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        company = companies_col.find_one({
            "CompanyID": company_id.upper(),
            "Password": password_hash,
            "Status": "Active"
        })
        return company
    
    @staticmethod
    def grant_access(company_id, college_id):
        """Grant company access to college data"""
        try:
            companies_col.update_one(
                {"CompanyID": company_id.upper()},
                {"$addToSet": {"AccessibleColleges": college_id.upper()}}
            )
            return True
        except Exception as e:
            print(f"Error granting access: {e}")
            return False
    
    @staticmethod
    def revoke_access(company_id, college_id):
        """Revoke company access to college data"""
        try:
            companies_col.update_one(
                {"CompanyID": company_id.upper()},
                {"$pull": {"AccessibleColleges": college_id.upper()}}
            )
            return True
        except Exception as e:
            print(f"Error revoking access: {e}")
            return False
    
    @staticmethod
    def can_access(company_id, college_id):
        """Check if company has access to college"""
        company = companies_col.find_one({"CompanyID": company_id.upper()})
        if company and "AccessibleColleges" in company:
            return college_id.upper() in company["AccessibleColleges"]
        return False


class AccessLog:
    @staticmethod
    def log(user_type, user_id, action, details=""):
        """Log access activity"""
        log = {
            "UserType": user_type,
            "UserID": user_id,
            "Action": action,
            "Details": details,
            "Timestamp": datetime.datetime.now()
        }
        try:
            access_logs_col.insert_one(log)
        except Exception as e:
            print(f"Error logging access: {e}")
    
    @staticmethod
    def get_logs(user_id=None, user_type=None, limit=100):
        """Get access logs"""
        query = {}
        if user_id:
            query["UserID"] = user_id
        if user_type:
            query["UserType"] = user_type
        
        return list(access_logs_col.find(query).sort("Timestamp", -1).limit(limit))