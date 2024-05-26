from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud
from app.schemas import ContactCreate, ContactUpdate, Contact as ContactSchema
from app.database import SessionLocal, engine
from app.models import Base


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#curl -X POST http://127.0.0.1:8000/contacts/ -H "Content-Type: application/json" -d '{"name": "John Doe", "email": "john@example.com"}'
@app.post("/contacts/", response_model=ContactSchema)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

#curl -X GET http://127.0.0.1:8000/contacts/
@app.get("/contacts/", response_model=List[ContactSchema])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    contacts = crud.get_contacts(db, skip=skip, limit=limit)
    return contacts

#curl -X GET http://127.0.0.1:8000/contacts/{contact_id}
@app.get("/contacts/{contact_id}", response_model=ContactSchema)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

#curl -X PUT http://127.0.0.1:8000/contacts/1 -H "Content-Type: application/json" -d "{\"first_name\": \"Updated Name\", \"last_name\": \"Updated Last Name\", \"email\": \"updated@example.com\", \"phone\": \"1234567890\", \"birthday\": \"1990-01-01\"}"
@app.put("/contacts/{contact_id}", response_model=ContactSchema)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    return crud.update_contact(db, contact_id, contact)

#curl -X DELETE http://127.0.0.1:8000/contacts/{contact_id}
@app.delete("/contacts/{contact_id}", response_model=ContactSchema)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    return crud.delete_contact(db, contact_id)

#curl -X GET "http://127.0.0.1:8000/contacts/search/?query=Jane"
@app.get("/contacts/search/", response_model=List[ContactSchema])
def search_contacts(query: str, db: Session = Depends(get_db)):
    return crud.search_contacts(db, query)

#curl -X GET http://127.0.0.1:8000/contacts/upcoming_birthdays/
@app.get("/contacts/upcoming_birthdays/", response_model=List[ContactSchema])
def upcoming_birthdays(db: Session = Depends(get_db)):
    return crud.get_upcoming_birthdays(db)
