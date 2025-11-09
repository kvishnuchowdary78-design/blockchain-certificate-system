from config import students_col, colleges_col, companies_col, certificates_col, access_logs_col
import bcrypt
import datetime
import logging

logger = logging.getLogger(__name__)

class Student:
    @staticmethod
    def create(usn, name, department, college_id, email, phone, password):
        """Create new student"""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            student = {
                "USN": usn.upper(),
                "Name": name,
                "Department": department,
                "CollegeID": college_id.upper(),
                "Email": email,
                "Phone": phone,
                "Password": password_hash.decode('utf-8'),
                "CreatedAt": datetime.datetime.now(),
                "Status": "Active"
            }
            
            result = students_col.insert_one(student)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error creating student: {e}")
            return None
    
    @staticmethod
    def authenticate(usn, password):
        """Authenticate student"""
        try:
            student = students_col.find_one({
                "USN": usn.upper(),
                "Status": "Active"
            })
            if student and bcrypt.checkpw(password.encode('utf-8'), 
                                         student['Password'].encode('utf-8')):
                return student
        except Exception as e:
            logger.error(f"Authentication error: {e}")
        return None
    
    @staticmethod
    def get_by_usn(usn):
        """Get student by USN"""
        return students_col.find_one({"USN": usn.upper()})
    
    @staticmethod
    def get_certificates(usn):
        """Get all certificates for a student"""
        return list(certificates_col.find({"USN": usn.upper()}).sort("CreatedAt", -1))


class College:
    @staticmethod
    def create(college_id, name, email, phone, address, password):
        """Create new college"""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            college = {
                "CollegeID": college_id.upper(),
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Address": address,
                "Password": password_hash.decode('utf-8'),
                "CreatedAt": datetime.datetime.now(),
                "Status": "Active"
            }
            
            result = colleges_col.insert_one(college)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error creating college: {e}")
            return None
    
    @staticmethod
    def authenticate(college_id, password):
        """Authenticate college"""
        try:
            college = colleges_col.find_one({
                "CollegeID": college_id.upper(),
                "Status": "Active"
            })
            if college and bcrypt.checkpw(password.encode('utf-8'), 
                                         college['Password'].encode('utf-8')):
                return college
        except Exception as e:
            logger.error(f"Authentication error: {e}")
        return None
    
    @staticmethod
    def get_students(college_id, department=None):
        """Get all students of a college"""
        query = {"CollegeID": college_id.upper()}
        if department:
            query["Department"] = department
        return list(students_col.find(query).sort("Name", 1))
    
    @staticmethod
    def get_certificates(college_id, department=None):
        """Get all certificates of a college"""
        query = {"CollegeID": college_id.upper()}
        if department:
            query["Department"] = department
        # Return sorted by creation date (newest first)
        return list(certificates_col.find(query).sort("CreatedAt", -1))


class Company:
    @staticmethod
    def create(company_id, name, email, phone, industry, password):
        """Create new company"""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            company = {
                "CompanyID": company_id.upper(),
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Industry": industry,
                "Password": password_hash.decode('utf-8'),
                "CreatedAt": datetime.datetime.now(),
                "Status": "Active",
                "AccessibleColleges": []
            }
            
            result = companies_col.insert_one(company)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error creating company: {e}")
            return None
    
    @staticmethod
    def authenticate(company_id, password):
        """Authenticate company"""
        try:
            company = companies_col.find_one({
                "CompanyID": company_id.upper(),
                "Status": "Active"
            })
            if company and bcrypt.checkpw(password.encode('utf-8'), 
                                         company['Password'].encode('utf-8')):
                return company
        except Exception as e:
            logger.error(f"Authentication error: {e}")
        return None
    
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
            logger.error(f"Error granting access: {e}")
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
            logger.error(f"Error revoking access: {e}")
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
            logger.error(f"Error logging access: {e}")
    
    @staticmethod
    def get_logs(user_id=None, user_type=None, limit=100):
        """Get access logs"""
        query = {}
        if user_id:
            query["UserID"] = user_id
        if user_type:
            query["UserType"] = user_type
        
        return list(access_logs_col.find(query).sort("Timestamp", -1).limit(limit))