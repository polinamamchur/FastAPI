from sqlalchemy.orm import Session
from app import models
from app.models import Contact, User
from app.schemas import ContactCreate, ContactUpdate, UserCreate
from datetime import date, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Users

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user from the database by their email address.

    Args:
        db (Session): The database session.
        email (str): The email address of the user.

    Returns:
        User: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """
    Create a new user in the database.

    Args:
        db (Session): The database session.
        user (UserCreate): The user creation schema containing user details.

    Returns:
        User: The newly created user object.
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_email(db: Session, email: str):
    """
    Verify a user's email address.

    Args:
        db (Session): The database session.
        email (str): The email address of the user.

    Returns:
        User: The verified user object.
    """
    user = get_user_by_email(db, email)
    if user:
        user.is_verified = True
        db.commit()
        db.refresh(user)
    return user

# Contacts

def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Retrieve a contact by its ID and owner ID.

    Args:
        db (Session): The database session.
        contact_id (int): The ID of the contact.
        user_id (int): The ID of the user who owns the contact.

    Returns:
        Contact: The contact object if found, otherwise None.
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of contacts for a user with pagination.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user who owns the contacts.
        skip (int, optional): The number of contacts to skip. Defaults to 0.
        limit (int, optional): The maximum number of contacts to return. Defaults to 10.

    Returns:
        List[Contact]: A list of contact objects.
    """
    return db.query(Contact).filter(Contact.owner_id == user_id).offset(skip).limit(limit).all()

def create_contact(db: Session, contact: ContactCreate, user_id: int):
    """
    Create a new contact for a user.

    Args:
        db (Session): The database session.
        contact (ContactCreate): The contact creation schema containing contact details.
        user_id (int): The ID of the user who owns the contact.

    Returns:
        Contact: The newly created contact object.
    """
    db_contact = Contact(**contact.dict(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user_id: int):
    """
    Update an existing contact for a user.

    Args:
        db (Session): The database session.
        contact_id (int): The ID of the contact to update.
        contact (ContactUpdate): The contact update schema containing updated contact details.
        user_id (int): The ID of the user who owns the contact.

    Returns:
        Contact: The updated contact object if found, otherwise None.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Delete a contact by its ID and owner ID.

    Args:
        db (Session): The database session.
        contact_id (int): The ID of the contact to delete.
        user_id (int): The ID of the user who owns the contact.

    Returns:
        Contact: The deleted contact object if found, otherwise None.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

def search_contacts(db: Session, query: str, user_id: int):
    """
    Search for contacts by query string within a user's contacts.
        query (str): The search query string.
        user_id (int): The ID of the user who owns the contacts.

    Returns:
        List[Contact]: A list of contact objects matching the search query.
    """
    return db.query(Contact).filter(
        Contact.owner_id == user_id,
        (Contact.first_name.contains(query) |
        Contact.last_name.contains(query) |
        Contact.email.contains(query))
    ).all()

def get_upcoming_birthdays(db: Session, user_id: int):
    """
    Retrieve contacts with birthdays within the upcoming week for a user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[Contact]: A list of contact objects with birthdays in the upcoming week.
    """
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(Contact.owner_id == user_id, Contact.birthday.between(today, next_week)).all()

def update_user_avatar(db: Session, user_id: int, avatar_url: str):
    """
    Update the avatar URL for a user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        avatar_url (str): The new avatar URL.

    Returns:
        User: The updated user object if found, otherwise None.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.avatar_url = avatar_url
        db.commit()
        db.refresh(db_user)
        return db_user

