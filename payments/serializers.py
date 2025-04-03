from rest_framework import serializers

from borrowings.serializers import BorrowingSerializer
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    borrowing = BorrowingSerializer()
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "borrowing",
            "status",
            "type",
            "amount",
            "session_id",
            "created_at",
        )
