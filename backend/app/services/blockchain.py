import hashlib
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from web3 import Web3
except ModuleNotFoundError:  # dev/env fallback
    Web3 = None

from app.core.config import settings

logger = logging.getLogger(__name__)



async def background_blockchain_anchor(ref_id: int, payload: dict, ref_type: str) -> None:
    """
    Async background task — anchors an attendance record hash to the blockchain
    and writes an audit row. Opens its own isolated DB session.
    """
    from app.db.database import SessionLocal  # sync session — safe in background thread
    from app.db.models.all_models import BlockchainAuditLog, SystemSetting

    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter_by(setting_key="blockchain_enabled").first()
        is_enabled = setting.setting_value.lower() == "true" if setting else False
        
        tx_hash = blockchain_service.anchor_record(ref_id, ref_type, payload, db_enabled=is_enabled)
        audit = BlockchainAuditLog(
            ref_id=ref_id,
            ref_type=ref_type,
            record_hash=blockchain_service.generate_record_hash(payload),
            tx_hash=tx_hash,
        )
        db.add(audit)
        db.commit()
    except Exception as exc:
        logger.error("Blockchain anchor failed for ref_id=%s ref_type=%s: %s", ref_id, ref_type, exc)
        db.rollback()
    finally:
        db.close()


class BlockchainService:
    def __init__(self):
        # IMPORTANT: keep imports and initialization non-blocking.
        # Do not create Web3 clients at import/constructor time in case
        # the provider is unreachable or libraries are missing.
        self._w3 = None
        self.contract = None  # Placeholder for deployed contract
        self._provider_url = settings.BLOCKCHAIN_URL or "http://127.0.0.1:8545"

    def _get_w3(self):
        """Lazy Web3 client creation."""
        global Web3
        if Web3 is None:
            return None
        if self._w3 is None:
            self._w3 = Web3(Web3.HTTPProvider(self._provider_url))
        return self._w3

    def _get_contract(self, w3):
        """Lazy contract instantiation."""
        if self.contract is not None:
            return self.contract
        if not settings.BLOCKCHAIN_CONTRACT_ADDRESS:
            return None
        try:
            import os
            abi_path = os.path.join(os.path.dirname(__file__), "..", "contracts", "AttendanceAudit.json")
            with open(abi_path, "r") as f:
                contract_data = json.load(f)
            abi = contract_data["abi"]
            self.contract = w3.eth.contract(address=w3.to_checksum_address(settings.BLOCKCHAIN_CONTRACT_ADDRESS), abi=abi)
        except Exception as e:
            logger.error(f"Failed to load contract ABI: {e}")
            return None
        return self.contract

    def generate_record_hash(self, payload: Dict[str, Any]) -> str:

        """
        Creates a deterministic SHA-256 hash of the attendance record.
        """
        # Ensure payload is sorted for deterministic hashing
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    def anchor_record(self, ref_id: int, ref_type: str, payload: Dict[str, Any], db_enabled: bool = False) -> str:
        """
        Anchors the record hash to the blockchain and returns the transaction hash.
        """
        record_hash = self.generate_record_hash(payload)
        
        w3 = self._get_w3()
        if w3 is None or not w3.is_connected() or not (settings.BLOCKCHAIN_ENABLED or db_enabled):
            logger.warning("Blockchain unavailable or disabled. Simulating anchoring.")
            return f"sim_tx_{record_hash[:16]}"
            
        contract = self._get_contract(w3)
        if not contract or not settings.BLOCKCHAIN_PRIVATE_KEY:
            logger.warning("Contract address or private key missing. Simulating anchoring.")
            return f"sim_tx_{record_hash[:16]}"
            
        try:
            account = w3.eth.account.from_key(settings.BLOCKCHAIN_PRIVATE_KEY)
            nonce = w3.eth.get_transaction_count(account.address)
            
            # Build the transaction
            tx = contract.functions.anchorRecord(ref_id, record_hash).build_transaction({
                'chainId': w3.eth.chain_id,
                'gas': 2000000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign and send
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=settings.BLOCKCHAIN_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return w3.to_hex(tx_hash)
        except Exception as e:
            logger.error(f"Blockchain transaction failed: {e}")
            return f"err_tx_{record_hash[:16]}"

    def verify_integrity(self, stored_hash: str, current_payload: Dict[str, Any]) -> bool:
        """
        Compares the current data against the 'sealed' hash.
        """
        current_hash = self.generate_record_hash(current_payload)
        return stored_hash == current_hash

# Expose a singleton instance for hashing/integrity checks.
# Unit tests expect `blockchain_service` to be non-None.
blockchain_service: BlockchainService = BlockchainService()


