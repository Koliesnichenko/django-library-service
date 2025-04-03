from decimal import Decimal
from django.test import TestCase


from books.models import Book
from books.serializers import BookSerializer


class BookSerializerTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=Decimal("2.50")
        )
        self.serializer = BookSerializer(instance=self.book)

    def test_serializer_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {"id", "title", "author", "cover", "inventory", "daily_fee", "image"}
        )

    def test_serializer_content(self):
        data = self.serializer.data
        self.assertEqual(data["id"], self.book.id)
        self.assertEqual(data["title"], self.book.title)
        self.assertEqual(data["author"], self.book.author)
        self.assertEqual(data["cover"], self.book.cover)
        self.assertEqual(data["inventory"], self.book.inventory)
        self.assertEqual(Decimal(data["daily_fee"]), self.book.daily_fee)

    def test_valid_data(self):
        valid_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": Decimal("2.50"),
            "image": None
        }
        serializer = BookSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        book = serializer.save()
        self.assertEqual(book.title, valid_data["title"])
        self.assertEqual(book.author, valid_data["author"])
        self.assertEqual(book.cover, valid_data["cover"])
        self.assertEqual(book.inventory, valid_data["inventory"])
        self.assertEqual(book.daily_fee, Decimal(valid_data["daily_fee"]))

    def test_invalid_data_inventory(self):
        invalid_data = {
            "title": "Invalid Book",
            "author": "Author",
            "cover": "SOFT",
            "inventory": 0,
            "daily_fee": Decimal("2.50")
        }
        serializer = BookSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertTrue(
            any("Inventory must be at least 1" in str(e) for e in serializer.errors["non_field_errors"])
        )

    def test_invalid_data_daily_fee(self):
        invalid_data = {
            "title": "Invalid Fee",
            "author": "Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": Decimal("0.00")
        }
        serializer = BookSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertTrue(
            any("Daily fee must be at least 0.01" in str(e) for e in serializer.errors["non_field_errors"])
        )

    def test_invalid_data_cover(self):
        invalid_data = {
            "title": "Invalid Cover",
            "author": "Author",
            "cover": "INVALID",
            "inventory": 5,
            "daily_fee": Decimal("2.50")
        }
        serializer = BookSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertFalse(serializer.is_valid())
        self.assertIn("cover", serializer.errors)