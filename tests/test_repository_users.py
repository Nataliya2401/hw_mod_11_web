import datetime
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel, TokenModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUsersRepo(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User()

    async def test_get_user_by_email(self):
        user = User()
        self.session.query().filter_by().first.return_value = user
        result = await get_user_by_email(email='test@gmail.com', db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(username='Koko', email='kkok@test.com', password='qwerty23')
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "roles"))

    async def test_update_token(self):
        self.session.query().filter().first.return_value = self.user
        self.session.commit.return_value = None
        token = 'refresh_token'
        await update_token(user=self.user, refresh_token=token, db=self.session)
        self.assertTrue(self.user.refresh_token)
        self.assertEqual(self.user.refresh_token, token)

    async def test_confirmed_user(self):
        self.session.query().filter_by().first.return_value = self.user
        self.session.commit.return_value = None
        email = 'kkok@test.com'
        await confirmed_email(email=email, db=self.session)
        self.assertTrue(self.user.confirmed)

    async def test_update_avatar(self):
        user = User(email="kkok@test.com", avatar="www.tort.com")
        self.session.query().filter_by().first.return_value = self.user
        url = 'www.vip.com'
        result = await update_avatar(email=self.user.email, url=url, db=self.session)
        self.assertEqual(result.avatar, url)
        self.assertEqual(result.avatar, self.user.avatar)
        self.assertTrue(user.avatar, "www.vip.com")


if __name__ == '__main__':
    unittest.main()


# class TestUsersRepo(unittest.IsolatedAsyncioTestCase):
#
#     def setUp(self):
#         self.session = MagicMock(spec=Session)
#         # self.user = User(id=1)
#         self.body = UserModel(
#             username='Nnnn',
#             email='test@test.com',
#             password='qwerty',
#             confirmed=False,
#             avatar='111222111')








