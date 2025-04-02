from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing
from user.models import User  # путь, который ты используешь у себя


class BorrowingModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author Name",
            cover="SOFT",
            inventory=5,
            daily_fee=Decimal("1.99")
        )
        self.expected_return_date = date.today() + timedelta(days=7)

    def test_borrowing_creation_decreases_inventory(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=self.expected_return_date
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.borrow_date, date.today())
        self.assertEqual(borrowing.expected_return_date, self.expected_return_date)
        self.assertIsNone(borrowing.actual_return_date)

    def test_return_book_sets_return_date_and_restores_inventory(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=self.expected_return_date
        )
        borrowing.return_book()
        borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertEqual(borrowing.actual_return_date, date.today())
        self.assertEqual(self.book.inventory, 5)

    def test_is_active_property(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=self.expected_return_date
        )
        self.assertTrue(borrowing.is_active())

        borrowing.return_book()
        self.assertFalse(borrowing.is_active())

    def test_str_representation(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=self.expected_return_date
        )
        expected_str = f"{self.user} borrowed '{self.book.title}' on {borrowing.borrow_date}"
        self.assertEqual(str(borrowing), expected_str)
