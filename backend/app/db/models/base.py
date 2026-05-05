from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import declarative_base
# class Base(DeclarativeBase):
#     pass
Base = declarative_base()

def NVARCHAR(length: int) -> String:
    """Unicode-safe VARCHAR — equivalent to SQL Server NVARCHAR."""
    return String(length)