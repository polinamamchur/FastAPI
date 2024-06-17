# test_crud.py
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app import crud, models, schemas
from app.database import Base, engine, get_db
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Override database URL for testing
DATABASE_URL = os.getenv("DATABASE_TEST_URL")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TestCRUD(unittest.TestCase):

    def setUp(self):
        # a new session for each test
        self.db = next(override_get_db())
        self.user_data = {"email": "test@example.com", "password": "testpassword"}
        self.user = crud.create_user(self.db, schemas.UserCreate(**self.user_data))

    def tearDown(self):
        # Clean up database after each test
        self.db.query(models.User).delete()
        self.db.commit()
        self.db.close()

    def test_create_user(self):
        created_user = self.db.query(models.User).filter(models.User.email == self.user_data["email"]).first()
        self.assertEqual(created_user.email, self.user_data["email"])

    def test_get_user_by_email(self):
        retrieved_user = crud.get_user_by_email(self.db, self.user_data["email"])
        self.assertEqual(retrieved_user.email, self.user_data["email"])

    def test_verify_user_email(self):
        verified_user = crud.verify_user_email(self.db, self.user_data["email"])
        self.assertTrue(verified_user.is_verified)

    def test_create_contact(self):
        contact_data = {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com"}
        created_contact = crud.create_contact(self.db, schemas.ContactCreate(**contact_data), self.user.id)
        self.assertEqual(created_contact.first_name, contact_data["first_name"])
        self.assertEqual(created_contact.last_name, contact_data["last_name"])

    def test_get_contact(self):
        contact_data = {"first_name": "Jane", "last_name": "Smith", "email": "jane.smith@example.com"}
        created_contact = crud.create_contact(self.db, schemas.ContactCreate(**contact_data), self.user.id)
        retrieved_contact = crud.get_contact(self.db, created_contact.id, self.user.id)
        self.assertEqual(retrieved_contact.first_name, contact_data["first_name"])
        self.assertEqual(retrieved_contact.last_name, contact_data["last_name"])

    def test_update_contact(self):
        contact_data = {"first_name": "Michael", "last_name": "Jordan", "email": "michael.jordan@example.com"}
        created_contact = crud.create_contact(self.db, schemas.ContactCreate(**contact_data), self.user.id)
        updated_contact_data = {"first_name": "LeBron", "last_name": "James"}
        updated_contact = crud.update_contact(self.db, created_contact.id, schemas.ContactUpdate(**updated_contact_data), self.user.id)
        self.assertEqual(updated_contact.first_name, updated_contact_data["first_name"])
        self.assertEqual(updated_contact.last_name, updated_contact_data["last_name"])

    def test_delete_contact(self):
        contact_data = {"first_name": "Stephen", "last_name": "Curry", "email": "stephen.curry@example.com"}
        created_contact = crud.create_contact(self.db, schemas.ContactCreate(**contact_data), self.user.id)
        deleted_contact = crud.delete_contact(self.db, created_contact.id, self.user.id)
        self.assertIsNone(deleted_contact)

    def test_search_contacts(self):
        contact_data_1 = {"first_name": "Alice", "last_name": "Johnson", "email": "alice.johnson@example.com"}
        contact_data_2 = {"first_name": "Bob", "last_name": "Williams", "email": "bob.williams@example.com"}
        crud.create_contact(self.db, schemas.ContactCreate(**contact_data_1), self.user.id)
        crud.create_contact(self.db, schemas.ContactCreate(**contact_data_2), self.user.id)
        search_results = crud.search_contacts(self.db, "Alice", self.user.id)
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].first_name, "Alice")

    def test_get_upcoming_birthdays(self):
        contact_data = {"first_name": "David", "last_name": "Robinson", "email": "david.robinson@example.com", "birthday": datetime.now() + timedelta(days=5)}
        created_contact = crud.create_contact(self.db, schemas.ContactCreate(**contact_data), self.user.id)
        upcoming_birthdays = crud.get_upcoming_birthdays(self.db, self.user.id)
        self.assertEqual(len(upcoming_birthdays), 1)
        self.assertEqual(upcoming_birthdays[0].first_name, "David")

    def test_update_user_avatar(self):
        new_avatar_url = "https://avatars.githubusercontent.com/u/14985020?v=4"
        updated_user = crud.update_user_avatar(self.db, self.user.id, new_avatar_url)
        self.assertEqual(updated_user.avatar_url, new_avatar_url)

if __name__ == "__main__":
    unittest.main()
