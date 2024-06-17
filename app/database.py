from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:polinamam25@localhost/contacts_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Create a new database session for a request.

    Yields:
        session: A SQLAlchemy database session object.

    Usage:
        Use this function with a context manager to get a database session:
        ```
        with get_db() as db:
            # Perform database operations using db
            ...
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
