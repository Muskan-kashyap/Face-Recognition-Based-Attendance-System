# Testing Strategy

## Testing Pyramid
```
        [E2E Tests]        ← Browser-level, few
      [Integration Tests]  ← Service boundary, moderate
    [Unit Tests]            ← Pure functions, many
```

## Unit Testing
**Framework**: `pytest` with `unittest.mock`

Unit tests cover:
- `compute_shift_status()` — Tests correct classification into On Time / Late / Early for various datetime combinations.
- `get_password_hash()` / `verify_password()` — Validates bcrypt round-trip.
- `BlockchainService.anchor_record()` — Mocks the Web3 RPC call; verifies simulation path when DB toggle is False.

### Example
```python
def test_shift_status_late(mock_shift, mock_time_9_10_am):
    status = compute_shift_status(check_in=mock_time_9_10_am, shift=mock_shift)
    assert status == "Late"  # grace_period_mins=5, shift starts 09:00
```

## Integration Testing
**Framework**: `pytest` + `httpx.AsyncClient` (no live DB; uses SQLite in-memory)

Integration tests cover:
- `POST /api/v1/auth/login` — Full JWT issuance.
- `POST /api/v1/attendance/check-in` — Mocks the AI service response; validates full DB write.
- `POST /api/v1/admin/settings/blockchain/toggle` — Validates RBAC; only SuperAdmin can toggle.

## Security Testing
- **SQL Injection**: All queries use SQLAlchemy ORM parameterized queries. Tested via `sqlmap` against local test instance.
- **JWT Tampering**: Tests attempt to modify the JWT payload and verify the server rejects signatures.
- **Privilege Escalation**: Tests verify that an Employee JWT cannot access SuperAdmin routes.

## Performance Testing
**Tool**: `locust` or `k6`
- Simulate 500 concurrent check-ins during the 9:00 AM morning spike.
- Target: P95 latency under 2500ms.
- Monitor: PostgreSQL connection pool exhaustion, Redis timeout errors.

## Test Coverage Expectations
| Module | Target Coverage |
|--------|----------------|
| `routers/` | > 85% |
| `services/` | > 80% |
| `crud/` | > 90% |
| `services/blockchain.py` | > 75% |
