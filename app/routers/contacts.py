from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi_limiter.depends import RateLimiter
from .. import schemas, crud, auth
from ..database import get_db

router = APIRouter(tags=["Contacts"])


@router.get("/contacts", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                  current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    """
    Retrieve contacts for the current user.

    Args:
        skip (int): Number of records to skip (default: 0).
        limit (int): Maximum number of records to retrieve (default: 10).
        db (Session): SQLAlchemy database session dependency.
        current_user (schemas.UserResponse): Current authenticated user.

    Returns:
        List[schemas.Contact]: List of contacts belonging to the current user.
    """
    contacts = crud.get_contacts(db, user_id=current_user.id, skip=skip, limit=limit)
    return contacts


@router.post("/contacts", response_model=schemas.Contact, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db),
                   current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    """
    Create a new contact for the current user.

    Args:
        contact (schemas.ContactCreate): Contact data to create.
        db (Session): SQLAlchemy database session dependency.
        current_user (schemas.UserResponse): Current authenticated user.

    Returns:
        schemas.Contact: Created contact data.
    """
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)


@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db),
                   current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    """
    Update an existing contact for the current user.

    Args:
        contact_id (int): ID of the contact to update.
        contact (schemas.ContactUpdate): Contact data to update.
        db (Session): SQLAlchemy database session dependency.
        current_user (schemas.UserResponse): Current authenticated user.

    Returns:
        schemas.Contact: Updated contact data.

    Raises:
        HTTPException: If the contact with the specified ID is not found.
    """
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.update_contact(db=db, contact_id=contact_id, contact=contact, user_id=current_user.id)


@router.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    """
    Delete an existing contact for the current user.

    Args:
        contact_id (int): ID of the contact to delete.
        db (Session): SQLAlchemy database session dependency.
        current_user (schemas.UserResponse): Current authenticated user.

    Returns:
        schemas.Contact: Deleted contact data.

    Raises:
        HTTPException: If the contact with the specified ID is not found.
    """
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.delete_contact(db=db, contact_id=contact_id, user_id=current_user.id)


@router.get("/contacts/search", response_model=List[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(get_db),
                    current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    """
    Search contacts for the current user based on a query string.

    Args:
        query (str): Search query string.
        db (Session): SQLAlchemy database session dependency.
        current_user (schemas.UserResponse): Current authenticated user.

    Returns:
        List[schemas.Contact]: List of contacts matching the search query.
    """
    return crud.search_contacts(db, query=query, user_id=current_user.id)


@router.get("/contacts/upcoming-birthdays", response_model=List[schemas.Contact])
def get_upcoming_birthdays(db: Session = Depends(get_db),
                           current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    """
    Retrieve contacts with upcoming birthdays for the current user.

    Args:
        db (Session): SQLAlchemy database session dependency.
        current_user (schemas.UserResponse): Current authenticated user.

    Returns:
        List[schemas.Contact]: List of contacts with upcoming birthdays.
    """
    return crud.get_upcoming_birthdays(db, user_id=current_user.id)
