from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

def NVARCHAR(length: int) -> String:
    """Unicode-safe VARCHAR — equivalent to SQL Server NVARCHAR."""
    return String(length)