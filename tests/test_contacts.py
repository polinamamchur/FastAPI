# tests/test_contacts.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import schemas

client = TestClient(app)



def test_create_contact(test_db_session):
    new_contact = schemas.ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1234567890",
        birthday="1990-01-01",
        additional_info="Some additional info"
    )
    response = test_db_session.app.post("/contacts/", json=new_contact.dict())

    assert response.status_code == 201
    created_contact = response.json()
    assert created_contact["first_name"] == new_contact.first_name
    assert created_contact["last_name"] == new_contact.last_name
    assert created_contact["email"] == new_contact.email
    assert created_contact["phone"] == new_contact.phone
    assert created_contact["birthday"] == new_contact.birthday
    assert created_contact["additional_info"] == new_contact.additional_info
    assert "id" in created_contact

# Тест для отримання списку контактів
def test_get_contacts(test_db_session):
    response = test_db_session.app.get("/contacts/")
    assert response.status_code == 200
    contacts = response.json()
    assert isinstance(contacts, list)


if __name__ == "__main__":
    pytest.main()
