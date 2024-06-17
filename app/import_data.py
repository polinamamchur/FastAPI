from app.database import SessionLocal, engine
from app import models


def init_db():
    """
    Initialize the database with initial data.

    This function populates the database with initial contacts.

    Usage:
        Call this function to initialize the database with initial data.
    """
    db = SessionLocal()
    contacts = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "birthday": "1980-01-01",
            "additional_info": "Friend from work"
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone": "0987654321",
            "birthday": "1990-02-02",
            "additional_info": "Met at a conference"
        },
    ]

    for contact in contacts:
        db_contact = models.Contact(**contact)
        db.add(db_contact)

    db.commit()
    db.close()


if __name__ == "__main__":
    # Create all database tables defined in models.Base
    models.Base.metadata.create_all(bind=engine)

    # Initialize the database with initial data
    init_db()
