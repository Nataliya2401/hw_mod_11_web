from datetime import datetime, date
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import create_contact, find_contacts_by_name, get_contacts, get_contact_by_email, \
    get_contact_by_id, remove_contact, \
    update_contact


class TestContactsRepo(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact = Contact(id=1)
        self.body = ContactModel(
            firstname='Nnnn',
            lastname='Testino',
            email='test@test.com',
            phone='111222111',
            birthday=date(1985, 7, 20),
            user_id=self.user.id,
            additionally='')

    async def test_get_contact(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query(Contact).filter().limit().offset().all.return_value = contacts
        result = await get_contacts(user=self.user, limit=10, offset=0, db=self.session)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        result = await create_contact(self.body, self.user, self.session)
        print(result)
        self.assertEqual(result.firstname, self.body.firstname)
        self.assertEqual(result.lastname, self.body.lastname)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.phone, self.body.phone)
        self.assertEqual(result.birthday, self.body.birthday)
        self.assertTrue(hasattr(result, 'user_id'))
        self.assertTrue(hasattr(result, 'id'))
        self.assertEqual(result.user_id, 1)
        self.assertEqual(result.additionally, self.body.additionally)

    async def test_update_contact(self):
        self.session.query().filter().first.return_value = self.contact
        result = await update_contact(contact_id=self.contact.id, body=self.body, user=self.user, db=self.session)
        self.assertEqual(result.id, self.contact.id)
        self.assertEqual(result.firstname, self.body.firstname)

    async def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=self.contact.id, body=self.body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_find_contact_by_email(self):
        contact = Contact(**self.body.dict())
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_email(email=self.body.email, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_find_contact_by_email_not_found(self):
        contact = Contact(**self.body.dict())
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_email(email=self.body.email, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_find_contact_by_id(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_find_contact_by_name(self):
        contacts = [Contact(**self.body.dict()), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await find_contacts_by_name(firstname=None, lastname=self.body.lastname, user=self.user,
                                             db=self.session)
        self.assertEqual(result, contacts)

    async def test_remove_contact(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)


if __name__ == '__main__':
    unittest.main()
