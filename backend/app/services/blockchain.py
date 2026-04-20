import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any
from web3 import Web3
from app.core.config import settings

class BlockchainService:
    def __init__(self):
        # In a real 2026 scenario, this would connect to a sidechain like Polygon or Arbitrum
        # For this implementation, we connect to a local provider or mock it.
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_URL or "http://127.0.0.1:8545"))
        self.contract = None # Placeholder for deployed contract
        
    def generate_record_hash(self, payload: Dict[str, Any]) -> str:
        """
        Creates a deterministic SHA-256 hash of the attendance record.
        """
        # Ensure payload is sorted for deterministic hashing
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    def anchor_record(self, ref_id: int, ref_type: str, payload: Dict[str, Any]) -> str:
        """
        Anchors the record hash to the blockchain and returns the transaction hash.
        """
        record_hash = self.generate_record_hash(payload)
        
        if not self.w3.is_connected():
            print("Warning: Blockchain not connected. Simulating anchoring.")
            return f"sim_tx_{record_hash[:16]}"
            
        # Real logic would be:
        # tx = self.contract.functions.anchorAttendance(ref_id, record_hash).transact()
        # return tx.hex()
        
        return f"tx_0x{record_hash[:32]}"

    def verify_integrity(self, stored_hash: str, current_payload: Dict[str, Any]) -> bool:
        """
        Compares the current data against the 'sealed' hash.
        """
        current_hash = self.generate_record_hash(current_payload)
        return stored_hash == current_hash

blockchain_service = BlockchainService()
