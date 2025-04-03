from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse


USER_CREATE_URL = reverse("users:create")
USER_MANAGE_URL = reverse("users:manage")


class CreateUserViewTest(APITestCase):
    def test_create_user_success(self):
        data = {
            "email": "testuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "Password123",
        }
        response = self.client.post(USER_CREATE_URL, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(get_user_model().objects.first().email, data["email"])

    def test_create_user_with_short_password(self):
        data = {
            "email": "testuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "123",
        }
        response = self.client.post(USER_CREATE_URL, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)


class ManageUserViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
            password="Password123",
        )
        self.token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_get_user_profile(self):
        response = self.client.get(USER_MANAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        self.assertEqual(response.data["last_name"], self.user.last_name)

    def test_update_user_profile(self):
        data = {"first_name": "Updated", "last_name": "User"}
        response = self.client.patch(USER_MANAGE_URL, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "User")

    def test_unauthorized_access(self):
        self.client.credentials()  # remove auth
        response = self.client.get(USER_MANAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
