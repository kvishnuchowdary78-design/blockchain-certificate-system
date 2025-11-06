import sys
import json
import random
import qrcode
import hashlib
import datetime
from config import certificates_col

VERIFICATION_URL = "http://127.0.0.1:5000/verify/"

class BlockChain:
    def __init__(self):
        pass
    
    def addCertificate(self, usn, student_name, department, college_id, 
                       academic_year, joining_date, end_date, cgpa, 
                       certfile, personality, skills=""):
        """Add certificate with blockchain"""
        
        data = {
            "USN": usn.upper(),
            "Studentname": student_name,
            "Department": department,
            "CollegeID": college_id.upper(),
            "AcademicYear": academic_year,
            "JoiningDate": joining_date,
            "EndDate": end_date,
            "CGPA": cgpa,
            "CertificateFile": certfile,
            "Personality": personality,
            "Skills": skills,
            "CreatedAt": str(datetime.datetime.now())
        }

        # Generate hash
        proHash = hashlib.sha256(str(data).encode()).hexdigest()
        print(f"Certificate Hash: {proHash}")
        data["hash"] = proHash

        # Store in MongoDB
        try:
            result = certificates_col.insert_one(data.copy())
            print(f"✓ Certificate stored in MongoDB with ID: {result.inserted_id}")
        except Exception as e:
            print(f"✗ MongoDB insertion failed: {e}")
            return None
        
        # Create blockchain block
        self.createBlock(data)
        
        # Generate QR code
        imgName = self.imgNameFormatting(student_name)
        self.createQR(proHash, imgName)
        
        return proHash
    
    def createBlock(self, data):
        """Create blockchain block"""
        try:
            # Read last block
            blocks = []
            try:
                with open('./NODES/N1/blockchain.json', 'r') as file:
                    for block in file:
                        blocks.append(block)
                
                if blocks:
                    preBlock = json.loads(blocks[-1])
                    index = preBlock["index"] + 1
                    preHash = hashlib.sha256(str(preBlock).encode()).hexdigest()
                else:
                    index = 1
                    preHash = "0"
            except FileNotFoundError:
                index = 1
                preHash = "0"

            transaction = {
                'index': index,
                'proof': random.randint(1, 1000),
                'previous_hash': preHash,
                'timestamp': str(datetime.datetime.now()),
                'data': str(data),
            }

            # Write to all nodes
            nodes = ['N1', 'N2', 'N3', 'N4']
            for node in nodes:
                with open(f"./NODES/{node}/blockchain.json", "a") as file:
                    file.write("\n" + json.dumps(transaction))
            
            print("✓ Block added to blockchain")
            
        except Exception as e:
            print(f"✗ Error creating block: {e}")

    def createQR(self, hashc, imgName):
        """Generate QR code"""
        try:
            img = qrcode.make(VERIFICATION_URL + hashc)
            img.save("./QRcodes/" + imgName)
            print(f"✓ QR Code generated: {imgName}")
        except Exception as e:
            print(f"✗ QR generation failed: {e}")

    def imgNameFormatting(self, student_name):
        """Format QR code filename"""
        dt = str(datetime.datetime.now())
        dt = dt.replace(" ", "_").replace("-", "_").replace(":", "_").replace(".", "_")
        return student_name.replace(" ", "_") + "_" + dt + ".png"

    def isBlockchainValid(self):
        """Verify blockchain integrity"""
        try:
            with open("./NODES/N1/blockchain.json", "r") as file:
                n1_hash = hashlib.sha256(str(file.read()).encode()).hexdigest()
            with open("./NODES/N2/blockchain.json", "r") as file:
                n2_hash = hashlib.sha256(str(file.read()).encode()).hexdigest()
            with open("./NODES/N3/blockchain.json", "r") as file:
                n3_hash = hashlib.sha256(str(file.read()).encode()).hexdigest()
            with open("./NODES/N4/blockchain.json", "r") as file:
                n4_hash = hashlib.sha256(str(file.read()).encode()).hexdigest()

            return n1_hash == n2_hash == n3_hash == n4_hash
        except:
            return False

    def getCertificateByHash(self, cert_hash):
        """Get certificate by hash"""
        try:
            certificate = certificates_col.find_one({"hash": cert_hash})
            return certificate
        except Exception as e:
            print(f"✗ MongoDB query failed: {e}")
            return None
    
    def getCertificateByUSN(self, usn):
        """Get certificate by USN"""
        try:
            certificates = list(certificates_col.find({"USN": usn.upper()}))
            return certificates
        except Exception as e:
            print(f"✗ MongoDB query failed: {e}")
            return []
    
    def searchCertificates(self, search_term, search_field="Studentname", college_id=None):
        """Search certificates"""
        try:
            query = {}
            
            if college_id:
                query["CollegeID"] = college_id.upper()
            
            if search_field == "all":
                query["$or"] = [
                    {"Studentname": {"$regex": search_term, "$options": "i"}},
                    {"USN": {"$regex": search_term, "$options": "i"}},
                    {"Department": {"$regex": search_term, "$options": "i"}}
                ]
            else:
                query[search_field] = {"$regex": search_term, "$options": "i"}
            
            results = list(certificates_col.find(query))
            return results
        except Exception as e:
            print(f"✗ Search failed: {e}")
            return []