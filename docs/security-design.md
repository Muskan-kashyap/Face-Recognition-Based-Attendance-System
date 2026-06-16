# Security Design

## 1. Zero-Knowledge Biometrics
The most significant security vector in this application is the theft of biometric data. To mitigate this:
* Raw images are **never** written to disk.
* Upon processing, the image is passed through the neural network to extract a 128-dimensional array of floats.
* The original image is immediately garbage collected from memory.
* It is mathematically impossible to reconstruct the original human face from the 128-dimensional embedding vector.

## 2. Authentication & JWT Management
* Passwords are hashed using `bcrypt` (via `passlib`).
* JWT tokens are signed using the `SECRET_KEY` configured in the `.env` file via `HS256`.
* **Logout & Invalidation**: Because JWTs are stateless, logout is handled by caching the JWT signature in a Redis "Blacklist" with an expiration equal to the JWT's remaining TTL.

## 3. Role-Based Access Control (RBAC)
The API strictly enforces role checks using FastAPI dependencies.
```python
def check_role(*allowed_roles):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role.name not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough privileges")
        return current_user
    return role_checker
```
* **SuperAdmin**: Global access.
* **Admin**: Cross-department access within a single `org_id`.
* **Manager**: Access limited to users sharing the same `dept_id`.
* **Employee**: Read-only access to their own records.

## 4. Blockchain Auditing
To prevent "Ghost Check-ins" (a DBA maliciously inserting a row into PostgreSQL), the system uses Web3. The data payload `SHA-256(user_id + check_in_time)` is signed using a private key and submitted to an Ethereum Smart Contract. 
If an auditor suspects foul play, they can pull the Ethereum transaction and verify that the blockchain hash matches the database hash. If they do not match, the database was tampered with.
