from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# For PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Hrhk@9090@postgresserver/db"
engine = create_engine(SQLALCHEMY_DATABASE_URL) 

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
