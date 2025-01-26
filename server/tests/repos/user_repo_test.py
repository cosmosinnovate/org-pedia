import unittest
from app.repo.user_repo import UserRepository
from app.models.models import User

class TestUserRepository(unittest.TestCase):

    def setUp(self):
        self.user_repo = UserRepository()
        self.test_user = User(id="user_id", name="Test User", email="testuser@example.com")

    def test_add_user(self):
        self.user_repo.add_user(self.test_user)
        user = self.user_repo.get_user_by_id("user_id")
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.email, "testuser@example.com")

    def test_get_user_by_id(self):
        self.user_repo.add_user(self.test_user)
        user = self.user_repo.get_user_by_id("user_id")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, "user_id")

    def test_remove_user(self):
        self.user_repo.add_user(self.test_user)
        self.user_repo.delete_user_by_id("user_id")
        user = self.user_repo.get_user_by_id("user_id")
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()