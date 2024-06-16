from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# Контакти
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class Contact(ContactBase):
    id: int

    class Config:
        orm_mode = True  # Використовується для сумісності з ORM моделями

# Користувачі
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserBase(BaseModel):
    email: EmailStr

class UserUpdate(UserBase):  # Додали новий клас UserUpdate з полем avatar_url
    avatar_url: Optional[str]

class UserResponse(UserBase):
    id: int
    is_verified: bool
    avatar_url: Optional[str]

    class Config:
        alias_generator = "from_attributes"


    class Config:
        alias_generator = "from_attributes"

# Токени
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
