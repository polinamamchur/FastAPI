from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from . import models, schemas, crud
from .database import SessionLocal, engine
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# Завантаження змінних середовища з файлу .env
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_secret_key')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

# Ініціалізація контексту для хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

#curl -X POST -H "Content-Type: application/json" -d "{\"email\": \"example@example.com\", \"password\": \"password123\"}" http://localhost:8000/register
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud.create_user(db=db, user=user)

#curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "username=example@example.com&password=password123" http://localhost:8000/token
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(days=7)
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

#curl -X GET -H "Authorization: Bearer {access_tocken}" http://localhost:8000/users/me
@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: schemas.UserResponse = Depends(get_current_user)):
    return current_user

@app.get("/contacts", response_model=list[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    contacts = crud.get_contacts(db, user_id=current_user.id, skip=skip, limit=limit)
    return contacts

@app.post("/contacts", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)

@app.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.update_contact(db=db, contact_id=contact_id, contact=contact, user_id=current_user.id)

@app.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.delete_contact(db=db, contact_id=contact_id, user_id=current_user.id)

@app.get("/contacts/search", response_model=list[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    return crud.search_contacts(db, query=query, user_id=current_user.id)

@app.get("/contacts/upcoming-birthdays", response_model=list[schemas.Contact])
def get_upcoming_birthdays(db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    return crud.get_upcoming_birthdays(db, user_id=current_user.id)
