from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from cloudinary.uploader import upload as cloudinary_upload
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import schemas, crud, auth
from ..database import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user (schemas.UserCreate): User registration data.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        schemas.UserResponse: Details of the registered user.

    Raises:
        HTTPException: If the email is already registered.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    db_user = crud.create_user(db=db, user=user)
    token = auth.generate_verification_token(user.email)
    verification_url = f"http://0.0.0.0:8000/api/verify-email?token={token}"
    auth.send_email(user.email, "Verify your email", f"Please verify your email: {verification_url}")
    return db_user

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get an access token for authentication.

    Args:
        db (Session): SQLAlchemy database session dependency.
        form_data (OAuth2PasswordRequestForm): Form data containing username (email) and password.

    Returns:
        schemas.Token: Access token details.

    Raises:
        HTTPException: If credentials are incorrect or email is not verified.
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(days=7)
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    """
    Get details of the current authenticated user.

    Args:
        current_user (schemas.UserResponse): Current authenticated user details.

    Returns:
        schemas.UserResponse: Details of the current authenticated user.
    """
    return current_user

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user email using a verification token.

    Args:
        token (str): Verification token sent to the user.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        dict: Confirmation message upon successful email verification.

    Raises:
        HTTPException: If user is not found.
    """
    email = auth.verify_verification_token(token)
    user = crud.verify_user_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Email verified successfully"}

@router.post("/upload-avatar", response_model=schemas.UserResponse)
def upload_avatar(
        avatar: UploadFile = File(...),
        current_user: schemas.UserResponse = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Upload a user avatar.

    Args:
        avatar (UploadFile): Uploaded avatar file.
        current_user (schemas.UserResponse): Current authenticated user details.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        schemas.UserResponse: Updated user details with avatar URL.
    """
    upload_result = cloudinary_upload(avatar.file)  # Assuming avatar.file is directly passed to cloudinary_upload
    updated_user = crud.update_user_avatar(
        db=db,
        user_id=current_user.id,
        avatar_url=upload_result['secure_url']  # Assuming secure_url field contains the avatar URL
    )
    return updated_user
