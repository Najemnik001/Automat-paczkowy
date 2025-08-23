from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserModelTest(TestCase):

    def test_create_user_with_default_role(self):
        user = User.objects.create_user(username="jan", usersurname="Test", password="test123")
        self.assertEqual(user.role, "client")
        self.assertEqual(str(user), "jan Test")

    def test_create_admin_user(self):
        user = User.objects.create_user(
            username="admin1",
            password="admin123",
            role="admin",
            usersurname="Kowalski"
        )
        self.assertEqual(user.role, "admin")
        self.assertEqual(str(user), "admin1 Kowalski")

    def test_create_courier_user(self):
        user = User.objects.create_user(
            username="kurier",
            password="kurier123",
            role="courier",
            usersurname="Nowak"
        )
        self.assertEqual(user.role, "courier")
        self.assertIn("Nowak", str(user))
