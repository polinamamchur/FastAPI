"""
Authentication and email utilities.

This module contains functions and utilities for handling authentication,
token generation, and email operations.
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
from . import schemas, crud, database
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
EMAIL_SECRET_KEY = os.getenv('EMAIL_SECRET_KEY')
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(EMAIL_SECRET_KEY)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta, optional): The time duration after which the token expires. Defaults to 15 minutes.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_verification_token(email: str) -> str:
    """
    Generate a verification token for email confirmation.

    Args:
        email (str): The email address to include in the token.

    Returns:
        str: The generated verification token.
    """
    return serializer.dumps(email, salt="email-confirm-salt")

def verify_verification_token(token: str) -> str:
    """
    Verify a given email verification token.

    Args:
        token (str): The token to verify.

    Raises:
        HTTPException: If the token is invalid or expired.

    Returns:
        str: The email address contained in the token.
    """
    try:
        email = serializer.loads(token, salt="email-confirm-salt", max_age=3600)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    return email

def send_email(to_email: str, subject: str, body: str):
    """
    Send an email.

    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email.
    """
    from_email = EMAIL_SENDER
    password = EMAIL_PASSWORD

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, password)
        server.sendmail(from_email, [to_email], msg.as_string())

def get_user(db: Session, email: str):
    """
    Retrieve a user by email from the database.

    Args:
        db (Session): The database session.
        email (str): The email address to search for.

    Returns:
        User: The user object if found, otherwise None.
    """
    return crud.get_user_by_email(db, email)

def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user.

    Args:
        db (Session): The database session.
        email (str): The email address of the user.
        password (str): The password of the user.

    Returns:
        User: The authenticated user object if successful, otherwise False.
    """
    user = get_user(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Get the current logged-in user.

    Args:
        token (str): The JWT token of the user.
        db (Session): The database session.

    Raises:
        HTTPException: If the token is invalid or the user is not found.

    Returns:
        User: The current logged-in user.
    """
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
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user
