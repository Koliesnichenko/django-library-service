from django.conf import settings
from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("EXPIRED", "Expired"),
    ]

    TYPE_CHOICES = [
        ("PAYMENT", "Payment"),
        ("FINE", "Fine")
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name="payments")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    session_url = models.URLField(max_length=1000)
    session_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.type} - {self.status}"
