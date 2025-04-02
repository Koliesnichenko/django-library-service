from django.test import TestCase
from django.db.utils import IntegrityError
from user.models import User


class UserModelTests(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "strongpassword123"

    def test_create_user_success(self):
        user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_success(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password=self.password
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password=self.password)

    def test_create_user_with_empty_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password=self.password)

    def test_create_user_with_duplicate_email_raises_integrity_error(self):
        User.objects.create_user(email=self.email, password=self.password)

        with self.assertRaises(IntegrityError):
            User.objects.create_user(email=self.email, password="newpass456")