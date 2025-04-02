from datetime import date, timedelta

from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from borrowings.models import Borrowing
from books.models import Book
from user.models import User
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    ReturnBorrowingSerializer,
)


class BorrowingSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            first_name="Test",
            last_name="User",
            password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=5,
            daily_fee=5.00
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7)
        )

    def test_borrowing_serializer_data(self):
        serializer = BorrowingSerializer(instance=self.borrowing)
        data = serializer.data

        self.assertIn("book", data)
        self.assertEqual(data["borrow_date"], str(self.borrowing.borrow_date))
        self.assertEqual(data["expected_return_date"], str(self.borrowing.expected_return_date))
        self.assertIsNone(data["actual_return_date"])


class BorrowingCreateSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            first_name="Test",
            last_name="User",
            password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=5,
            daily_fee=5.00
        )

    def test_valid_borrowing_create(self):
        expected_return_date = date.today() + timedelta(days=7)
        data = {
            "expected_return_date": expected_return_date,
            "book": self.book.id,
        }
        serializer = BorrowingCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_borrowing_create_with_unavailable_book(self):
        self.book.inventory = 0
        self.book.save()

        data = {
            "expected_return_date": date.today() + timedelta(days=7),
            "book": self.book.id,
        }
        serializer = BorrowingCreateSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class ReturnBorrowingSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            first_name="Test",
            last_name="User",
            password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=5,
            daily_fee=5.00
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7)
        )

    def test_valid_return(self):
        serializer = ReturnBorrowingSerializer(instance=self.borrowing, data={})
        self.assertTrue(serializer.is_valid())

    def test_already_returned(self):
        self.borrowing.actual_return_date = date.today()
        self.borrowing.save()

        serializer = ReturnBorrowingSerializer(instance=self.borrowing, data={})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
