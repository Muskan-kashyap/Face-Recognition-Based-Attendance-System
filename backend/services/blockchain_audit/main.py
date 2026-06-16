import json
import hashlib
import logging
from typing import Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from web3 import Web3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlockchainAuditService")

app = FastAPI(title="Blockchain Audit Service", version="1.0.0")

# Database configurations
# DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/face_attendance_db"
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/face_attendance_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request schemas
class AnchorPayload(BaseModel):
    ref_id: int
    ref_type: str
    log_data: Dict[str, Any]

class VerifyRequest(BaseModel):
    ref_id: int
    ref_type: str
    current_data: Dict[str, Any]

# Web3 setup
BLOCKCHAIN_URL = "http://127.0.0.1:8545" # Ganache or local Polygon RPC
w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))

# Mock contract details (ABI and Address) for scaffolding.
# In production, these are loaded from build artifacts.
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "refId", "type": "uint256"},
            {"internalType": "string", "name": "recordHash", "type": "string"}
        ],
        "name": "anchorRecord",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "refId", "type": "uint256"},
            {"internalType": "string", "name": "recordHash", "type": "string"}
        ],
        "name": "verifyRecord",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]
CONTRACT_ADDRESS = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"

def generate_deterministic_hash(payload: Dict[str, Any]) -> str:
    """
    Computes a sorted deterministic SHA-256 hash of a dictionary.
    """
    sorted_str = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(sorted_str.encode()).hexdigest()

@app.post("/api/v1/blockchain/anchor")
def anchor_log(req: AnchorPayload, db: Session = Depends(get_db)):
    # 1. Compute deterministic hash
    record_hash = generate_deterministic_hash(req.log_data)
    
    tx_hash = f"0x_sim_tx_{record_hash[:32]}"
    block_num = 999999
    
    # 2. Connect to local Ganache/Polygon node if available, otherwise fallback
    # if w3.is_connected():
    #     try:
    #         # Simple simulation using local accounts
    #         contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    #         # In a real environment, transaction is signed using private keys:
    #         # tx = contract.functions.anchorRecord(req.ref_id, record_hash).build_transaction(...)
    #         # signed_tx = w3.eth.account.sign_transaction(tx, private_key=SECRET_KEY)
    #         # tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
    #         logger.info(f"Successfully anchored record {req.ref_id} on chain. Hash: {record_hash}")
    #     except Exception as e:
    #         logger.warning(f"Failed to post to contract, falling back to simulated anchoring: {e}")
    # else:
    #     logger.warning("Blockchain node offline. Running simulated transaction anchoring.")

    # 3. Store record in audit table
    try:
        db.execute(
            text(
                "INSERT INTO blockchain_audit_logs (ref_id, ref_type, record_hash, tx_hash, block_number) "
                "VALUES (:ref_id, :ref_type, :record_hash, :tx_hash, :block_num)"
            ),
            {
                "ref_id": req.ref_id,
                "ref_type": req.ref_type,
                "record_hash": record_hash,
                "tx_hash": tx_hash,
                "block_num": block_num
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database write error: {e}")

    return {
        "status": "anchored",
        "ref_id": req.ref_id,
        "record_hash": record_hash,
        "tx_hash": tx_hash,
        "block_number": block_num
    }

@app.post("/api/v1/blockchain/verify")
def verify_log_integrity(req: VerifyRequest, db: Session = Depends(get_db)):
    # 1. Fetch details from audit table
    audit_row = db.execute(
        text("SELECT record_hash, tx_hash, block_number FROM blockchain_audit_logs WHERE ref_id = :ref_id AND ref_type = :ref_type"),
        {"ref_id": req.ref_id, "ref_type": req.ref_type}
    ).fetchone()
    
    if not audit_row:
        raise HTTPException(status_code=404, detail="No audit log found on chain for this record")
    
    # 2. Compute hash from current db parameters
    current_hash = generate_deterministic_hash(req.current_data)
    
    # 3. Perform comparison (Integrity check)
    is_intact = (audit_row.record_hash == current_hash)
    
    return {
        "ref_id": req.ref_id,
        "anchored_hash": audit_row.record_hash,
        "current_hash": current_hash,
        "integrity_passed": is_intact,
        "transaction_hash": audit_row.tx_hash,
        "block_number": audit_row.block_number
    }
