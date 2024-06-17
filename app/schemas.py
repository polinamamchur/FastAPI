from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# Contacts
class ContactBase(BaseModel):
    """
    Base schema for contact data.

    Defines common attributes for creating and updating contacts.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (EmailStr): The email address of the contact.
        phone (str): The phone number of the contact.
        birthday (date): The birthday of the contact.
        additional_info (str, optional): Additional information about the contact.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str] = None

class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.

    Inherits attributes from ContactBase.
    """
    pass

class ContactUpdate(ContactBase):
    """
    Schema for updating an existing contact.

    Inherits attributes from ContactBase.
    """
    pass

class Contact(ContactBase):
    """
    Schema representing a contact including its ID.

    Inherits attributes from ContactBase and adds an 'id' attribute.

    Attributes:
        id (int): The unique identifier of the contact.
    """
    id: int

    class Config:
        orm_mode = True  # Used for compatibility with ORM models

# Users
class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Attributes:
        email (EmailStr): The email address of the user.
        password (str): The password of the user.
    """
    email: EmailStr
    password: str

class UserBase(BaseModel):
    """
    Base schema for user data.

    Defines common attributes for user information.

    Attributes:
        email (EmailStr): The email address of the user.
    """
    email: EmailStr

class UserUpdate(UserBase):
    """
    Schema for updating user information.

    Inherits attributes from UserBase and adds 'avatar_url'.

    Attributes:
        avatar_url (str, optional): URL of the user's avatar image.
    """
    avatar_url: Optional[str]

class UserResponse(UserBase):
    """
    Schema for responding with user data.

    Inherits attributes from UserBase and adds 'id', 'is_verified', and 'avatar_url'.

    Attributes:
        id (int): The unique identifier of the user.
        is_verified (bool): Indicates if the user's email has been verified.
        avatar_url (str, optional): URL of the user's avatar image.
    """
    id: int
    is_verified: bool
    avatar_url: Optional[str]

    class Config:
        alias_generator = "from_attributes"  # Configure alias generation for attribute names

# Tokens
class Token(BaseModel):
    """
    Schema for representing an authentication token.

    Attributes:
        access_token (str): The access token for authentication.
        refresh_token (str): The refresh token for authentication.
        token_type (str): The type of token (e.g., "bearer").
    """
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Schema for token data.

    Attributes:
        email (str, optional): The email associated with the token.
    """
    email: Optional[str] = None
