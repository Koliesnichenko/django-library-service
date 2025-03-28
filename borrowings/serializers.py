from datetime import date

from django.contrib.auth import get_user_model
from rest_framework import serializers
from borrowings.models import Borrowing
from books.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "book", "expected_return_date")

    def validate(self, attrs):
        book = attrs.get("book")
        if book.inventory < 1:
            raise serializers.ValidationError("This book is not available now.")
        return attrs


class ReturnBorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
        read_only_fields = ("id", "actual_return_date")

    def validate(self, attrs):
        borrowing = self.instance
        if borrowing.actual_return_date:
            raise serializers.ValidationError("This book is already returned.")
        return attrs
