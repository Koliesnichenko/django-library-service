from datetime import date, timedelta
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from borrowings.models import Borrowing
from books.models import Book
from user.models import User


BORROWINGS_LIST_URL = reverse("borrowings:borrowing-list")


def get_borrowing_detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


class BorrowingViewSetTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com", password="password123",
            first_name="Test", last_name="User"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="admin123",
            first_name="Admin", last_name="User"
        )
        self.book = Book.objects.create(
            title="Test Book", author="Author",
            inventory=5, daily_fee=5.00
        )
        self.client.force_authenticate(user=self.user)

    def test_list_borrowings_for_user(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7)
        )
        response = self.client.get(BORROWINGS_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_filter_by_user_id(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7)
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"{BORROWINGS_LIST_URL}?user_id={self.user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_borrowing_successfully(self):
        payload = {
            "expected_return_date": date.today() + timedelta(days=7),
            "book": self.book.id,
        }
        response = self.client.post(BORROWINGS_LIST_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["book"], self.book.id)

    def test_create_borrowing_fails_when_inventory_empty(self):
        self.book.inventory = 0
        self.book.save()
        payload = {
            "expected_return_date": date.today() + timedelta(days=7),
            "book": self.book.id,
        }
        response = self.client.post(BORROWINGS_LIST_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_book_success(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7)
        )
        response = self.client.post(f"{get_borrowing_detail_url(borrowing.id)}return/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

    def test_return_already_returned_book(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
            actual_return_date=date.today()
        )
        response = self.client.post(f"{get_borrowing_detail_url(borrowing.id)}return/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "This book has already been returned.")

    def test_is_active_filter(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7)
        )
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
            actual_return_date=date.today()
        )
        active_resp = self.client.get(f"{BORROWINGS_LIST_URL}?is_active=true")
        returned_resp = self.client.get(f"{BORROWINGS_LIST_URL}?is_active=false")
        self.assertEqual(len(active_resp.data), 1)
        self.assertEqual(len(returned_resp.data), 1)
