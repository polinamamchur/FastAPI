from sqlalchemy import Column, Integer, String, Date, Boolean
from app.database import Base

class Contact(Base):
    """
    Database model for a contact.

    Represents a contact stored in the 'contacts' table.

    Attributes:
        id (int): The primary key ID of the contact.
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact (must be unique).
        phone (str): The phone number of the contact.
        birthday (date): The birthday of the contact.
        additional_info (str, optional): Additional information about the contact.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    birthday = Column(Date)
    additional_info = Column(String, nullable=True)


class User(Base):
    """
    Database model for a user.

    Represents a user stored in the 'users' table.

    Attributes:
        id (int): The primary key ID of the user.
        email (str): The email address of the user (must be unique).
        hashed_password (str): The hashed password of the user.
        is_verified (bool): Indicates if the user's email has been verified (default: False).
        avatar_url (str, optional): URL of the user's avatar image.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
