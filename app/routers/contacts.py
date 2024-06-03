from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, auth
from ..database import get_db

router = APIRouter()

@router.get("/contacts", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    contacts = crud.get_contacts(db, user_id=current_user.id, skip=skip, limit=limit)
    return contacts

@router.post("/contacts", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)

@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.update_contact(db=db, contact_id=contact_id, contact=contact, user_id=current_user.id)

@router.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.delete_contact(db=db, contact_id=contact_id, user_id=current_user.id)

@router.get("/contacts/search", response_model=List[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    return crud.search_contacts(db, query=query, user_id=current_user.id)

@router.get("/contacts/upcoming-birthdays", response_model=List[schemas.Contact])
def get_upcoming_birthdays(db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    return crud.get_upcoming_birthdays(db, user_id=current_user.id)
