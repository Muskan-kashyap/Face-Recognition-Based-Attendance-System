import pytest
from app.services.blockchain import blockchain_service

def test_generate_record_hash():
    payload = {"user_id": 1, "status": "on_time"}
    hash1 = blockchain_service.generate_record_hash(payload)
    hash2 = blockchain_service.generate_record_hash(payload)
    
    assert hash1 == hash2
    assert len(hash1) == 64

def test_verify_integrity_success():
    payload = {"user_id": 1, "status": "on_time"}
    stored_hash = blockchain_service.generate_record_hash(payload)
    
    assert blockchain_service.verify_integrity(stored_hash, payload) is True

def test_verify_integrity_failure():
    payload = {"user_id": 1, "status": "on_time"}
    stored_hash = blockchain_service.generate_record_hash(payload)
    
    # Tamper with data
    tampered_payload = {"user_id": 1, "status": "late"}
    assert blockchain_service.verify_integrity(stored_hash, tampered_payload) is False
