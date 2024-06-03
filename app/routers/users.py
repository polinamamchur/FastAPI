from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
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
    return crud.create_user(db=db, user=user)

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
