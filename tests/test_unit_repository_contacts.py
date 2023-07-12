import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts, get_contact_by_id, search_contacts_by_birthday, create, update, remove
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.test_contact = Contact(
            id=1,
            first_name='Oleksandr',
            last_name='Gnatiuk',
            email='oleksandr@gmail.com',
            phone_number="+380678742845",
            birthday="1976-03-07"
        )

    async def test_get_contacts_birthdays(self):
        today = datetime.today()

        # Mock Contact objects with different birthdays
        contacts = [Contact(birthday=(today + timedelta(days=i)).strftime("%Y-%m-%d")) for i in range(5)]

        # Set the last contact's birthday to be outside the 7-day period
        contacts[-1].birthday = (today + timedelta(days=8)).strftime("%Y-%m-%d")

        # Mock the query method of the session to return the contacts
        self.session.query().filter().limit().offset().all.return_value = contacts

        result = await search_contacts_by_birthday(limit=10, offset=0, user=self.user, db=self.session)
        print(result)

        self.assertEqual(len(result), 4)  # Only the first 4 contacts should be within the 7-day period

    async def test_get_contact_id(self):
        contacts = [self.test_contact, Contact(), Contact()]
        query_mock = self.session.query(Contact).filter().first.return_value = contacts
        result = await get_contact_by_id(contact_id=self.test_contact.id, user=self.user, db=self.session)
        self.assertEqual(result[0], self.test_contact)

    async def test_get_contacts(self):
        contacts = [Contact() for _ in range(5)]
        query_mock = self.session.query(Contact).limit().offset().all.return_value = contacts
        result = await get_contacts(limit=10, offset=0, first_name="", last_name="", email="", user=self.user,
                                    db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_firstname(self):
        contacts = [self.test_contact, Contact(), Contact()]
        # query_mock = self.session.query(Contact).filter_by().limit().offset().all.return_value = contacts

        """ it was a problem with this mock. ChatGPT recommends such decision:"""
        query_mock = self.session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = contacts
        result = await get_contacts(limit=10, offset=0, first_name=self.test_contact.first_name,
                                    last_name="", email="", user=self.user,
                                    db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_lastname(self):
        contacts = [self.test_contact, Contact(), Contact()]
        query_mock = self.session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = contacts
        result = await get_contacts(limit=10, offset=0, first_name="",
                                    last_name=self.test_contact.last_name, email="", user=self.user,
                                    db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_email(self):
        contacts = [self.test_contact, Contact(), Contact()]
        query_mock = self.session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = contacts
        result = await get_contacts(limit=10, offset=0, first_name="", last_name="",
                                    email=self.test_contact.email, user=self.user,
                                    db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_firstname_and_lastname(self):
        contacts = [self.test_contact, Contact(), Contact()]
        query_mock = self.session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.union.return_value = query_mock
        query_mock.all.return_value = contacts
        result = await get_contacts(limit=10, offset=0, first_name=self.test_contact.first_name,
                                    last_name=self.test_contact.last_name,
                                    email="", user=self.user,
                                    db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_firstname_and_email(self):
        contacts = [self.test_contact, Contact(), Contact()]
        query_mock = self.session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.union.return_value = query_mock
        query_mock.all.return_value = contacts
        result = await get_contacts(limit=10, offset=0, first_name=self.test_contact.first_name, last_name="",
                                    email=self.test_contact.email, user=self.user,
                                    db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_lastname_and_email(self):
        contacts = [self.test_contact, Contact(), Contact()]
        query_mock = self.session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.union.return_value = query_mock
        query_mock.all.return_value = contacts
        result = await get_contacts(limit=10, offset=0, first_name="",
                                    last_name=self.test_contact.last_name,
                                    email=self.test_contact.email, user=self.user,
                                    db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_firstname_and_lastname_and_email(self):
        contacts = [self.test_contact, Contact(), Contact()]
        query_mock = self.session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.union.return_value = query_mock
        query_mock.all.return_value = contacts
        result = await get_contacts(limit=10, offset=0, first_name=self.test_contact.first_name,
                                    last_name=self.test_contact.last_name,
                                    email=self.test_contact.email, user=self.user,
                                    db=self.session)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactModel(first_name=self.test_contact.first_name,
                            last_name=self.test_contact.last_name,
                            email=self.test_contact.email,
                            phone_number=self.test_contact.phone_number,
                            birthday=self.test_contact.birthday,
                            additional_data="")
        result = await create(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        contact = self.test_contact
        body = ContactModel(first_name=self.test_contact.first_name,
                            last_name=self.test_contact.last_name,
                            email=self.test_contact.email,
                            phone_number=self.test_contact.phone_number,
                            birthday=self.test_contact.birthday,
                            additional_data="")
        self.session.query().filter().first.return_value = contact
        result = await update(contact_id=self.test_contact.id, body=body, db=self.session, user=self.user)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactModel(first_name=self.test_contact.first_name,
                            last_name=self.test_contact.last_name,
                            email=self.test_contact.email,
                            phone_number=self.test_contact.phone_number,
                            birthday=self.test_contact.birthday,
                            additional_data="")
        self.session.query().filter().first.return_value = None
        result = await update(contact_id=self.test_contact.id, body=body, db=self.session, user=self.user)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
