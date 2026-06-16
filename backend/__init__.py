"""Top-level package initializer.

This file intentionally avoids importing SQLAlchemy model definitions at import time.

Those imports can create duplicate SQLAlchemy MetaData/table registrations when
multiple import paths exist (e.g., `backend.app...` vs `app...`).
"""

__all__ = []

