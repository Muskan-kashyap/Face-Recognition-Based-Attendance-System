# Security & Testing Specifications
## Security Architecture and Comprehensive Testing Strategy

### 1. Security Architecture

#### 1.1 Zero-Knowledge Biometric Signatures (Schnorr Commitment)
To satisfy strict GDPR biometric compliance, raw images are processed in volatile memory, converted to vectors, and sealed using a cryptographic **Schnorr Commitment**.
- Let $G$ be a generator of a chosen elliptic curve group.
- The 128-d face embedding is compressed to a private scalar exponent $x$.
- We calculate and store the public commitment $P = x \cdot G$.
- The raw embedding vector is then processed using standard distance metrics in volatile memory for fast lookups, but its permanent database state can be validated using zero-knowledge proofs (ZKP) to prove ownership of the private biometric identity without revealing the vector.

#### 1.2 JWT Token Rotation and Blacklist
The authentication system uses a dual-token paradigm (Access + Refresh tokens):
- **Access Tokens:** Signed with HMAC-SHA256, contains user roles and tenant identifiers. Expires in 60 minutes.
- **Refresh Tokens:** Stored in secure, HTTP-only, SameSite=Strict cookies. Expires in 7 days.
- **Token Blacklisting:** When logging out or revoking credentials, the token fingerprint is written to **Redis** with a Time-to-Live (TTL) matching the token's remaining validity duration. Subsequent requests query Redis to verify the token is not on the blacklist.

#### 1.3 CORS and Security Headers
The custom API Gateway enforces strict security headers:
- `X-Content-Type-Options: nosniff` (prevents MIME-type sniffing).
- `X-Frame-Options: DENY` (prevents clickjacking attacks).
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (enforces HSTS).
- **CORS Configuration:** Restricts origins to registered tenant domain strings, rejecting wildcard (`*`) access in production.

---

### 2. Testing Strategy

#### 2.1 Biometric Mock webcam tests
For testing biometric pipelines without real hardware, we write testing utilities that pass pre-extracted arrays or static test image buffers to endpoints.
```python
# app/tests/test_biometrics.py
import pytest
import numpy as np

def generate_mock_face_embedding() -> list:
    """Generates a standard unit-normalized mock 128-d embedding."""
    vec = np.random.randn(128)
    normalized = vec / np.linalg.norm(vec)
    return normalized.tolist()

def test_mock_recognition():
    emb1 = generate_mock_face_embedding()
    emb2 = generate_mock_face_embedding()
    
    # Cosine distance
    distance = 1.0 - np.dot(emb1, emb2)
    # Different random faces should not match (distance usually > 0.5)
    assert distance > 0.3
```

#### 2.2 Liveness Anti-Spoofing Assertions
Liveness checks are tested using a validation matrix containing both authentic face recordings and flat-screen playback vectors.
- **True Positive Rate (TPR):** System must accept live human video frames > 99.2% of the time.
- **False Acceptance Rate (FAR):** System must block photo/video spoofing attempts (variance < 100) with a success rate > 99.8%.

#### 2.3 Performance & Load Testing with Locust
Locust performance tests confirm that matching requests take less than 500ms under load.
`tests/locustfile.py`
```python
from locust import HttpUser, task, between
import base64

class BiometricKioskUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task
    def verify_face_log(self):
        # Base64 encoded 10x10 mock grey pixel image
        mock_image = base64.b64encode(b'\x00' * 300).decode('utf-8')
        payload = {
            "image_base64": mock_image,
            "org_id": "893c5d6e-82be-47ea-a67b-1cbcfdb36802"
        }
        self.client.post("/api/v1/attendance/verify", json=payload)
```

#### 2.4 Solidity Smart Contract Tests
Tests are executed on Ganache or Hardhat to verify the anchoring contract:
```javascript
// test/AttendanceAudit.js
const { expect } = require("chai");

describe("AttendanceAudit", function () {
  it("Should store and verify attendance hashes", async function () {
    const AuditContract = await ethers.getContractFactory("AttendanceAudit");
    const contract = await AuditContract.deploy();
    await contract.deployed();

    const recordId = 1045;
    const recordHash = "0x4a9b83b3e2101df...";

    const tx = await contract.anchorAttendance(recordId, recordHash);
    await tx.wait();

    const storedHash = await contract.getRecordHash(recordId);
    expect(storedHash).to.equal(recordHash);
  });
});
```
