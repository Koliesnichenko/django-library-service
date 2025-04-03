from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError

from books.models import Book


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=Decimal("2.50")
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Test Author")
        self.assertEqual(self.book.cover, "HARD")
        self.assertEqual(self.book.inventory, 10)
        self.assertEqual(self.book.daily_fee, Decimal("2.50"))

    def test_str_representation(self):
        self.assertEqual(str(self.book), "Test Book - Test Author")

    def test_inventory_validator(self):
        book = Book(
            title="Invalid",
            author="Author",
            cover="SOFT",
            inventory=0,
            daily_fee=Decimal("5.00")
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_daily_fee_validator(self):
        book = Book(
            title="Invalid",
            author="Author",
            cover="SOFT",
            inventory=5,
            daily_fee=Decimal("0.00")
        )
        with self.assertRaises(ValidationError):
            book.full_clean()
