from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from cloudinary.uploader import upload as cloudinary_upload
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import schemas, crud, auth
from ..database import get_db

router = APIRouter()

#curl -X POST -H "Content-Type: application/json" -d "{\"email\": \"john@example.com\", \"password\": \"password123\"}" http://127.0.0.1:8000/api/register
@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    db_user = crud.create_user(db=db, user=user)
    token = auth.generate_verification_token(user.email)
    verification_url = f"http://0.0.0.0:8000/api/verify-email?token={token}"
    auth.send_email(user.email, "Verify your email", f"Please verify your email: {verification_url}")
    return db_user

#curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "username=john@example.com&password=password123" http://127.0.0.1:8000/api/token
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
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

#curl -X GET -H "Authorization: Bearer {access_token}" http://127.0.0.1:8000/api/users/me
@router.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    return current_user

#curl -X GET http://127.0.0.1:8000/api/verify-email?token={token}
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
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
    # Завантаження аватара на Cloudinary
    upload_result = cloudinary_upload(avatar.file)  # Передайте файл напряму до cloudinary_upload

    # Оновлення користувача з URL аватара
    updated_user = crud.update_user_avatar(
        db=db,
        user_id=current_user.id,
        avatar_url=upload_result['secure_url']  # Припустимо, що поле secure_url містить URL аватара
    )

    return updated_user
