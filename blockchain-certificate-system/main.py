import base64
import json
import os
import logging
from io import BytesIO
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, Response
from blockchain import BlockChain
from models import Student, College, Company, AccessLog
from config import certificates_col, students_col, colleges_col, companies_col
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security configuration
app.secret_key = os.getenv('SECRET_KEY', os.urandom(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Helper function to check login
def require_login(user_type=None):
    """Decorator to check if user is logged in"""
    if 'user_id' not in session or 'user_type' not in session:
        return False
    if user_type and session.get('user_type') != user_type:
        return False
    return True

@app.route("/")
def index():
    return render_template('index.html')

# ==================== STUDENT ROUTES ====================

@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        usn = request.form["usn"]
        password = request.form["password"]
        
        student = Student.authenticate(usn, password)
        
        if student:
            session["user_id"] = student["USN"]
            session["user_type"] = "student"
            session["user_name"] = student["Name"]
            
            AccessLog.log("Student", student["USN"], "Login")
            
            flash(f"Welcome {student['Name']}!", "success")
            return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid USN or Password", "danger")
    
    return render_template('student_login.html')

@app.route("/student/dashboard")
def student_dashboard():
    if not require_login("student"):
        flash("Please login first", "warning")
        return redirect(url_for("student_login"))
    
    usn = session.get("user_id")
    student = Student.get_by_usn(usn)
    certificates = Student.get_certificates(usn)
    
    return render_template('student_dashboard.html', 
                         student=student, 
                         certificates=certificates)

@app.route("/student/view_certificate/<cert_hash>")
def student_view_certificate(cert_hash):
    if not require_login("student"):
        flash("Please login first", "warning")
        return redirect(url_for("student_login"))
    
    bc = BlockChain()
    certificate = bc.getCertificateByHash(cert_hash)
    
    if certificate and certificate["USN"] == session.get("user_id"):
        return render_template('student_view_certificate.html', cert=certificate)
    else:
        flash("Certificate not found or access denied", "danger")
        return redirect(url_for("student_dashboard"))

# ==================== COLLEGE ROUTES ====================

@app.route("/college/login", methods=["GET", "POST"])
def college_login():
    if request.method == "POST":
        college_id = request.form["college_id"]
        password = request.form["password"]
        
        college = College.authenticate(college_id, password)
        
        if college:
            session["user_id"] = college["CollegeID"]
            session["user_type"] = "college"
            session["user_name"] = college["Name"]
            
            AccessLog.log("College", college["CollegeID"], "Login")
            
            flash(f"Welcome {college['Name']}!", "success")
            return redirect(url_for("college_dashboard"))
        else:
            flash("Invalid College ID or Password", "danger")
    
    return render_template('college_login.html')

@app.route("/college/dashboard")
def college_dashboard():
    if not require_login("college"):
        flash("Please login first", "warning")
        return redirect(url_for("college_login"))
    
    college_id = session.get("user_id")
    students = College.get_students(college_id)
    certificates = College.get_certificates(college_id)
    
    # Group by department
    departments = {}
    for student in students:
        dept = student.get("Department", "Unknown")
        if dept not in departments:
            departments[dept] = 0
        departments[dept] += 1
    
    return render_template('college_dashboard.html', 
                         students=students,
                         certificates=certificates,
                         departments=departments)

@app.route("/college/add_student", methods=["GET", "POST"])
def college_add_student():
    if not require_login("college"):
        flash("Please login first", "warning")
        return redirect(url_for("college_login"))
    
    if request.method == "POST":
        college_id = session.get("user_id")
        
        usn = request.form["usn"]
        name = request.form["name"]
        department = request.form["department"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        
        result = Student.create(usn, name, department, college_id, email, phone, password)
        
        if result:
            AccessLog.log("College", college_id, f"Added student {usn}")
            flash(f"Student {name} added successfully!", "success")
            return redirect(url_for("college_dashboard"))
        else:
            flash("Failed to add student. USN might already exist.", "danger")
    
    return render_template('college_add_student.html')

@app.route("/college/add_certificate", methods=["GET", "POST"])
def college_add_certificate():
    if not require_login("college"):
        flash("Please login first", "warning")
        return redirect(url_for("college_login"))
    
    college_id = session.get("user_id")
    
    if request.method == "POST":
        # File validation
        file = request.files.get('certfile')
        
        if not file or file.filename == '':
            flash("No file selected", "danger")
            return redirect(url_for('college_add_certificate'))
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            flash("Only PDF files are supported", "danger")
            return redirect(url_for('college_add_certificate'))
        
        # Read file content
        try:
            certfile_content = file.read()
            
            # Check file size (additional check beyond MAX_CONTENT_LENGTH)
            file_size = len(certfile_content)
            max_size = 10 * 1024 * 1024  # 10MB
            
            if file_size > max_size:
                flash(f"File too large. Maximum size is {max_size // (1024*1024)}MB", "danger")
                return redirect(url_for('college_add_certificate'))
            
            if file_size == 0:
                flash("File is empty. Please upload a valid PDF file.", "danger")
                return redirect(url_for('college_add_certificate'))
            
            # Basic PDF validation - check magic bytes
            if not certfile_content.startswith(b'%PDF'):
                flash("Invalid PDF file. Please upload a valid PDF document.", "danger")
                return redirect(url_for('college_add_certificate'))
            
            # Encode file to base64
            certfile = base64.b64encode(certfile_content).decode()
            
            logger.info(f"File validated: {file.filename}, Size: {file_size} bytes")
            
        except Exception as e:
            logger.error(f"File read error: {e}")
            flash("Error reading file. Please try again.", "danger")
            return redirect(url_for('college_add_certificate'))
        
        # Get form data
        try:
            usn = request.form["usn"]
            student_name = request.form["student_name"]
            department = request.form["department"]
            academic_year = request.form["academic_year"]
            joining_date = request.form["joining_date"]
            end_date = request.form["end_date"]
            cgpa = request.form["cgpa"]
            personality = request.form["personality"]
            skills = request.form.get("skills", "")
            
            # Validate CGPA
            try:
                cgpa_float = float(cgpa)
                if cgpa_float < 0 or cgpa_float > 10:
                    flash("CGPA must be between 0 and 10", "danger")
                    return redirect(url_for('college_add_certificate'))
            except ValueError:
                flash("Invalid CGPA value", "danger")
                return redirect(url_for('college_add_certificate'))
            
        except KeyError as e:
            flash(f"Missing required field: {e}", "danger")
            return redirect(url_for('college_add_certificate'))
        
        # Create certificate
        bc = BlockChain()
        try:
            cert_hash = bc.addCertificate(
                usn, student_name, department, college_id,
                academic_year, joining_date, end_date, cgpa,
                certfile, personality, skills
            )
            
            if cert_hash:
                AccessLog.log("College", college_id, f"Added certificate for {usn}")
                flash("Certificate added successfully!", "success")
                logger.info(f"Certificate created with hash: {cert_hash}")
                return redirect(url_for('college_dashboard'))
            else:
                flash("Failed to add certificate. Please try again.", "danger")
                logger.error("Certificate creation returned None")
        except Exception as e:
            logger.error(f"Certificate creation error: {e}")
            flash("An error occurred while creating certificate. Please try again.", "danger")
    
    # Get students of this college for dropdown
    students = College.get_students(college_id)
    return render_template('college_add_certificate.html', students=students)

@app.route("/college/view_students")
def college_view_students():
    if not require_login("college"):
        flash("Please login first", "warning")
        return redirect(url_for("college_login"))
    
    college_id = session.get("user_id")
    department = request.args.get("department", None)
    
    students = College.get_students(college_id, department)
    
    return render_template('college_view_students.html', students=students)

@app.route("/college/manage_access", methods=["GET", "POST"])
def college_manage_access():
    if not require_login("college"):
        flash("Please login first", "warning")
        return redirect(url_for("college_login"))
    
    college_id = session.get("user_id")
    
    if request.method == "POST":
        company_id = request.form["company_id"]
        action = request.form["action"]
        
        if action == "grant":
            if Company.grant_access(company_id, college_id):
                AccessLog.log("College", college_id, f"Granted access to company {company_id}")
                flash(f"Access granted to company {company_id}", "success")
            else:
                flash("Failed to grant access", "danger")
        elif action == "revoke":
            if Company.revoke_access(company_id, college_id):
                AccessLog.log("College", college_id, f"Revoked access from company {company_id}")
                flash(f"Access revoked from company {company_id}", "success")
            else:
                flash("Failed to revoke access", "danger")
        
        return redirect(url_for("college_manage_access"))
    
    # Get all companies
    all_companies = list(companies_col.find())
    
    # Get companies with access
    companies_with_access = []
    for company in all_companies:
        if "AccessibleColleges" in company and college_id.upper() in company["AccessibleColleges"]:
            companies_with_access.append(company)
    
    return render_template('college_manage_access.html', 
                         all_companies=all_companies,
                         companies_with_access=companies_with_access)

# ==================== COMPANY ROUTES ====================

@app.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        company_id = request.form["company_id"]
        password = request.form["password"]
        
        company = Company.authenticate(company_id, password)
        
        if company:
            session["user_id"] = company["CompanyID"]
            session["user_type"] = "company"
            session["user_name"] = company["Name"]
            
            AccessLog.log("Company", company["CompanyID"], "Login")
            
            flash(f"Welcome {company['Name']}!", "success")
            return redirect(url_for("company_dashboard"))
        else:
            flash("Invalid Company ID or Password", "danger")
    
    return render_template('company_login.html')

@app.route("/company/dashboard")
def company_dashboard():
    if not require_login("company"):
        flash("Please login first", "warning")
        return redirect(url_for("company_login"))
    
    company_id = session.get("user_id")
    company = companies_col.find_one({"CompanyID": company_id})
    
    accessible_colleges = company.get("AccessibleColleges", [])
    
    return render_template('company_dashboard.html', 
                         company=company,
                         accessible_colleges=accessible_colleges)

@app.route("/company/verify_student", methods=["GET", "POST"])
def company_verify_student():
    if not require_login("company"):
        flash("Please login first", "warning")
        return redirect(url_for("company_login"))
    
    company_id = session.get("user_id")
    
    if request.method == "POST":
        search_type = request.form["search_type"]
        search_value = request.form["search_value"]
        
        bc = BlockChain()
        results = []
        
        if search_type == "usn":
            results = bc.getCertificateByUSN(search_value)
        elif search_type == "hash":
            cert = bc.getCertificateByHash(search_value)
            if cert:
                results = [cert]
        
        # Filter by accessible colleges
        company = companies_col.find_one({"CompanyID": company_id})
        accessible_colleges = company.get("AccessibleColleges", [])
        
        filtered_results = [r for r in results if r.get("CollegeID") in accessible_colleges]
        
        if filtered_results:
            AccessLog.log("Company", company_id, f"Verified student {search_value}")
        
        return render_template('company_verify_results.html', results=filtered_results)
    
    return render_template('company_verify_student.html')

@app.route("/company/view_students")
def company_view_students():
    if not require_login("company"):
        flash("Please login first", "warning")
        return redirect(url_for("company_login"))
    
    company_id = session.get("user_id")
    company = companies_col.find_one({"CompanyID": company_id})
    accessible_colleges = company.get("AccessibleColleges", [])
    
    # Get all students from accessible colleges
    students = list(students_col.find({"CollegeID": {"$in": accessible_colleges}}))
    
    return render_template('company_view_students.html', students=students)

# ==================== COMMON ROUTES ====================

@app.route("/verify/<cert_hash>")
def public_verify(cert_hash):
    """Public certificate verification"""
    bc = BlockChain()
    certificate = bc.getCertificateByHash(cert_hash)
    
    if certificate:
        return render_template('verify_success.html', cert=certificate)
    else:
        return render_template('verify_fraud.html')

@app.route("/logout")
def logout():
    user_type = session.get("user_type")
    user_id = session.get("user_id")
    
    if user_id and user_type:
        AccessLog.log(user_type.capitalize(), user_id, "Logout")
    
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("index"))

@app.route("/download_certificate/<cert_hash>")
def download_certificate(cert_hash):
    bc = BlockChain()
    certificate = bc.getCertificateByHash(cert_hash)
    
    if certificate and certificate.get("CertificateFile"):
        try:
            bytes_io = BytesIO(base64.b64decode(certificate["CertificateFile"]))
            return send_file(
                bytes_io,
                download_name=f'certificate_{certificate["USN"]}.pdf',
                as_attachment=True,
                mimetype='application/pdf'
            )
        except Exception as e:
            logger.error(f"Error downloading certificate: {e}")
            flash(f"Error downloading certificate: {e}", "danger")
            return redirect(request.referrer or url_for("index"))
    else:
        flash("Certificate file not found", "danger")
        return redirect(request.referrer or url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)