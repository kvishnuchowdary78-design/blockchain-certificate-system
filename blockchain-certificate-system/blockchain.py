import sys
import json
import os
import qrcode
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
        
        # Generate QR code
        imgName = self.imgNameFormatting(student_name)
        self.createQR(proHash, imgName)
        
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

    def createQR(self, hashc, imgName):
        """Generate QR code"""
        try:
            img = qrcode.make(VERIFICATION_URL + hashc)
            qr_path = "./QRcodes/" + imgName
            img.save(qr_path)
            logger.info(f"✓ QR Code generated: {imgName}")
        except Exception as e:
            logger.error(f"✗ QR generation failed: {e}")

    def imgNameFormatting(self, student_name):
        """Format QR code filename"""
        dt = str(datetime.datetime.now())
        dt = dt.replace(" ", "_").replace("-", "_").replace(":", "_").replace(".", "_")
        return student_name.replace(" ", "_") + "_" + dt + ".png"

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
        """Get certificate by USN"""
        try:
            certificates = list(certificates_col.find({"USN": usn.upper()}))
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