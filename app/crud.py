from sqlalchemy.orm import Session
from app.models import Contact, User
from app.schemas import ContactCreate, ContactUpdate, UserCreate
from datetime import date, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Користувачі
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Контакти
def get_contact(db: Session, contact_id: int, user_id: int):
    return db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(Contact).filter(Contact.owner_id == user_id).offset(skip).limit(limit).all()

def create_contact(db: Session, contact: ContactCreate, user_id: int):
    db_contact = Contact(**contact.dict(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user_id: int):
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

def search_contacts(db: Session, query: str, user_id: int):
    return db.query(Contact).filter(
        Contact.owner_id == user_id,
        (Contact.first_name.contains(query) |
        Contact.last_name.contains(query) |
        Contact.email.contains(query))
    ).all()

def get_upcoming_birthdays(db: Session, user_id: int):
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(Contact.owner_id == user_id, Contact.birthday.between(today, next_week)).all()
