import sys
import json
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import hashlib
import datetime
import logging
from threading import Lock
from config import certificates_col

VERIFICATION_URL = "http://127.0.0.1:5000/verify/"

logger = logging.getLogger(__name__)

class BlockchainError(Exception):
    """Custom blockchain exception"""
    pass

class BlockChain:
    _lock = Lock()
    
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
        logger.info(f"Certificate Hash: {proHash}")
        data["hash"] = proHash

        # Store in MongoDB
        try:
            result = certificates_col.insert_one(data.copy())
            logger.info(f"✓ Certificate stored in MongoDB with ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"✗ MongoDB insertion failed: {e}")
            return None
        
        # Create blockchain block
        try:
            self.createBlock(data)
        except BlockchainError as e:
            logger.error(f"✗ Blockchain creation failed: {e}")
            # Rollback MongoDB insert
            certificates_col.delete_one({"hash": proHash})
            return None
        
        # Generate QR code with enhanced design
        imgName = self.imgNameFormatting(student_name)
        qr_path = self.createEnhancedQR(proHash, student_name, usn, imgName)
        
        logger.info(f"✓ Certificate created successfully")
        logger.info(f"✓ QR Code: {qr_path}")
        logger.info(f"✓ Verification URL: {VERIFICATION_URL}{proHash}")
        
        return proHash
    
    def read_chain(self, node='N1'):
        """Read blockchain from file"""
        try:
            filepath = f'./NODES/{node}/blockchain.json'
            if not os.path.exists(filepath):
                return []
            
            with open(filepath, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in blockchain file: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading blockchain: {e}")
            return []
    
    def write_chain(self, chain):
        """Write blockchain to all nodes atomically"""
        nodes = ['N1', 'N2', 'N3', 'N4']
        
        for node in nodes:
            filepath = f'./NODES/{node}/blockchain.json'
            temp_filepath = filepath + '.tmp'
            
            try:
                # Write to temporary file
                with open(temp_filepath, 'w') as f:
                    json.dump(chain, f, indent=2)
                
                # Atomic rename
                os.replace(temp_filepath, filepath)
            except Exception as e:
                logger.error(f"Error writing to node {node}: {e}")
                # Clean up temp file
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                raise BlockchainError(f"Failed to write to node {node}")
    
    def createBlock(self, data):
        """Create blockchain block with proper locking"""
        with self._lock:
            try:
                # Read current chain
                chain = self.read_chain('N1')
                
                if chain:
                    preBlock = chain[-1]
                    index = preBlock["index"] + 1
                    preHash = hashlib.sha256(
                        json.dumps(preBlock, sort_keys=True).encode()
                    ).hexdigest()
                else:
                    index = 1
                    preHash = "0"

                # Create new block
                transaction = {
                    'index': index,
                    'proof': self.proof_of_work(preHash, str(data)),
                    'previous_hash': preHash,
                    'timestamp': str(datetime.datetime.now()),
                    'data': str(data),
                }
                
                # Validate block
                if not self.is_valid_block(transaction, preBlock if chain else None):
                    raise BlockchainError("Invalid block created")
                
                # Add to chain
                chain.append(transaction)
                
                # Write to all nodes
                self.write_chain(chain)
                
                logger.info("✓ Block added to blockchain")
                
            except BlockchainError:
                raise
            except Exception as e:
                logger.exception("Error creating block")
                raise BlockchainError(f"Failed to create block: {e}")
    
    def proof_of_work(self, previous_hash, data, difficulty=4):
        """Simple proof-of-work algorithm"""
        proof = 0
        while True:
            hash_attempt = hashlib.sha256(
                f"{previous_hash}{data}{proof}".encode()
            ).hexdigest()
            if hash_attempt[:difficulty] == "0" * difficulty:
                return proof
            proof += 1
            # Safety limit
            if proof > 1000000:
                raise BlockchainError("Proof-of-work failed")
    
    def is_valid_block(self, block, previous_block):
        """Validate a block"""
        if previous_block:
            if block['index'] != previous_block['index'] + 1:
                logger.error("Invalid block index")
                return False
            
            expected_hash = hashlib.sha256(
                json.dumps(previous_block, sort_keys=True).encode()
            ).hexdigest()
            
            if block['previous_hash'] != expected_hash:
                logger.error("Invalid previous hash")
                return False
        
        return True

    def createEnhancedQR(self, hashc, student_name, usn, imgName):
        """Generate enhanced QR code with certificate info"""
        try:
            # Ensure QRcodes directory exists
            os.makedirs("./QRcodes", exist_ok=True)
            
            # Create QR code with high error correction
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(VERIFICATION_URL + hashc)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Create a larger image with text
            img_width = 600
            img_height = 700
            img = Image.new('RGB', (img_width, img_height), 'white')
            
            # Resize and paste QR code
            qr_img = qr_img.resize((400, 400))
            img.paste(qr_img, (100, 50))
            
            # Draw text
            draw = ImageDraw.Draw(img)
            
            try:
                # Try to use a nicer font
                title_font = ImageFont.truetype("arial.ttf", 30)
                text_font = ImageFont.truetype("arial.ttf", 20)
                small_font = ImageFont.truetype("arial.ttf", 14)
            except:
                # Fallback to default font
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Title
            title = "CERTIFICATE VERIFICATION"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((img_width - title_width) / 2, 10), title, fill='#667eea', font=title_font)
            
            # Student info
            y_offset = 470
            draw.text((50, y_offset), f"Student: {student_name}", fill='black', font=text_font)
            draw.text((50, y_offset + 35), f"USN: {usn}", fill='black', font=text_font)
            
            # Hash (truncated)
            draw.text((50, y_offset + 70), f"Hash: {hashc[:32]}...", fill='#666', font=small_font)
            
            # Instructions
            inst_text = "Scan to verify certificate on blockchain"
            inst_bbox = draw.textbbox((0, 0), inst_text, font=small_font)
            inst_width = inst_bbox[2] - inst_bbox[0]
            draw.text(((img_width - inst_width) / 2, y_offset + 110), inst_text, fill='#999', font=small_font)
            
            # Verification URL
            url_text = f"{VERIFICATION_URL[:30]}..."
            url_bbox = draw.textbbox((0, 0), url_text, font=small_font)
            url_width = url_bbox[2] - url_bbox[0]
            draw.text(((img_width - url_width) / 2, y_offset + 135), url_text, fill='#999', font=small_font)
            
            # Save image
            qr_path = "./QRcodes/" + imgName
            img.save(qr_path)
            
            logger.info(f"✓ Enhanced QR Code generated: {imgName}")
            return qr_path
            
        except Exception as e:
            logger.error(f"✗ QR generation failed: {e}")
            # Fallback to simple QR
            try:
                img = qrcode.make(VERIFICATION_URL + hashc)
                qr_path = "./QRcodes/" + imgName
                img.save(qr_path)
                logger.info(f"✓ Simple QR Code generated: {imgName}")
                return qr_path
            except Exception as e2:
                logger.error(f"✗ Fallback QR generation also failed: {e2}")
                return None

    def imgNameFormatting(self, student_name):
        """Format QR code filename"""
        dt = str(datetime.datetime.now())
        dt = dt.replace(" ", "_").replace("-", "_").replace(":", "_").replace(".", "_")
        safe_name = student_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        return f"{safe_name}_{dt}.png"

    def isBlockchainValid(self):
        """Verify blockchain integrity across all nodes"""
        try:
            hashes = []
            for i in range(1, 5):
                chain = self.read_chain(f'N{i}')
                chain_hash = hashlib.sha256(
                    json.dumps(chain, sort_keys=True).encode()
                ).hexdigest()
                hashes.append(chain_hash)
            
            # All hashes should be identical
            return len(set(hashes)) == 1
        except Exception as e:
            logger.error(f"Error validating blockchain: {e}")
            return False

    def getCertificateByHash(self, cert_hash):
        """Get certificate by hash"""
        try:
            certificate = certificates_col.find_one({"hash": cert_hash})
            return certificate
        except Exception as e:
            logger.error(f"✗ MongoDB query failed: {e}")
            return None
    
    def getCertificateByUSN(self, usn):
        """Get all certificates by USN"""
        try:
            certificates = list(certificates_col.find({"USN": usn.upper()}))
            return certificates
        except Exception as e:
            logger.error(f"✗ MongoDB query failed: {e}")
            return []
    
    def getCertificatesByCollegeID(self, college_id):
        """Get all certificates by college ID"""
        try:
            certificates = list(certificates_col.find({"CollegeID": college_id.upper()}))
            return certificates
        except Exception as e:
            logger.error(f"✗ MongoDB query failed: {e}")
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
            logger.error(f"✗ Search failed: {e}")
            return []