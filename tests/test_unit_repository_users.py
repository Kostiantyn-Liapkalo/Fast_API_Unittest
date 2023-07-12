import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import UserModel
from src.repository.users import (get_user_by_email, create_user, update_token, confirmed_email)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(
            id=1,
            username='test_user_',
            email='user1@meta.ua',
            password='qwerty',
            role='user',
            confirmed=True,
        )
        self.contact_test = Contact(
            id=1,
            first_name='Taras',
            last_name='Shevchenko',
            email='taras@mail.com',
            birthday='2000-05-12',
        )

    async def test_get_user_by_email(self):
        user = self.user
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body = UserModel(
            username=self.user.username,
            email=self.user.email,
            password=self.user.password,
        )
        result = await create_user(body=body, db=self.session)

        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_confirmed_email(self):
        result = await confirmed_email(email=self.user.email, db=self.session)
        self.assertIsNone(result)

    async def test_update_token(self):
        user = self.user
        token = None
        result = await update_token(user=user, token=token, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
   