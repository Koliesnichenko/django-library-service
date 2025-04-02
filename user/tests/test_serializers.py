from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


USER_CREATE_URL = reverse("users:create")
USER_MANAGE_URL = reverse("users:manage")


class UserSerializerTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

    def test_create_user_with_valid_data(self):
        data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newpassword123",
        }
        response = self.client.post(USER_CREATE_URL, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_user = get_user_model().objects.get(email=data["email"])
        self.assertTrue(created_user.check_password(data["password"]))

    def test_create_user_without_password(self):
        data = {
            "email": "nopassword@example.com",
            "first_name": "No",
            "last_name": "Pass",
        }
        response = self.client.post(USER_CREATE_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_invalid_email(self):
        data = {
            "email": "invalidemail",
            "first_name": "Invalid",
            "last_name": "Email",
            "password": "validpass123",
        }
        response = self.client.post(USER_CREATE_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_short_password(self):
        data = {
            "email": "shortpass@example.com",
            "first_name": "Short",
            "last_name": "Password",
            "password": "123",
        }
        response = self.client.post(USER_CREATE_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile(self):
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "password": "newsecurepassword",
        }
        response = self.client.patch(USER_MANAGE_URL, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertTrue(self.user.check_password("newsecurepassword"))

    def test_update_user_without_password(self):
        update_data = {"first_name": "Updated"}
        response = self.client.patch(USER_MANAGE_URL, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertTrue(self.user.check_password(self.user_data["password"]))