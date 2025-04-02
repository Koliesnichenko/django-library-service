from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase

from books.models import Book
from user.models import User
from books.serializers import BookSerializer


BOOKS_LIST_URL = reverse("books:books-list")


def get_book_detail_url(book_id):
    return reverse("books:books-detail", args=[book_id])


class BookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            first_name="John",
            last_name="Doe"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="admin123",
            first_name="Admin",
            last_name="User"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="SOFT",
            inventory=10,
            daily_fee=Decimal("1.50")
        )

    def test_list_books_authenticated(self):
        """Test: authenticated user can list books (should return 200)."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(BOOKS_LIST_URL)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_books_unauthenticated(self):
        """Test: unauthenticated user can list books (AllowAny)."""
        response = self.client.get(BOOKS_LIST_URL)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_book_authenticated(self):
        """Test: authenticated user can retrieve book details."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_book_detail_url(self.book.id))

        serializer = BookSerializer(self.book)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_book_unauthenticated(self):
        """Test: unauthenticated user can retrieve book details (AllowAny)."""
        response = self.client.get(get_book_detail_url(self.book.id))

        serializer = BookSerializer(self.book)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book_as_admin(self):
        """Test: admin can create books."""
        self.client.force_authenticate(user=self.admin)
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": "2.00",
        }
        response = self.client.post(BOOKS_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title=payload["title"]).exists())

    def test_create_book_as_user(self):
        """Test: regular user cannot create books."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "Unauthorized Book",
            "author": "Unauthorized Author",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": "1.00",
        }
        response = self.client.post(BOOKS_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Book.objects.filter(title=payload["title"]).exists())

    def test_update_book_as_admin(self):
        """Test: admin can update a book."""
        self.client.force_authenticate(user=self.admin)
        payload = {"title": "Updated Book Title"}

        response = self.client.patch(
            get_book_detail_url(self.book.id),
            payload
        )
        self.book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book.title, payload["title"])

    def test_update_book_as_user(self):
        """Test: regular user cannot update a book."""
        self.client.force_authenticate(user=self.user)
        payload = {"title": "Hacked Title"}

        response = self.client.patch(
            get_book_detail_url(self.book.id),
            payload
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.book.refresh_from_db()
        self.assertNotEqual(self.book.title, payload["title"])

    def test_delete_book_as_admin(self):
        """Test: admin can delete a book."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(get_book_detail_url(self.book.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())

    def test_delete_book_as_user(self):
        """Test: regular user cannot delete a book."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(get_book_detail_url(self.book.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=self.book.id).exists())
