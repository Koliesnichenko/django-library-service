from datetime import date

from django.conf import settings
from django.db import models, transaction

from books.models import Book

FINE_MULT = 2


class Borrowing(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.book.inventory -= 1
            self.book.save()
        super().save(*args, **kwargs)

    def return_book(self):
        if not self.actual_return_date:
            self.actual_return_date = date.today()
            self.book.inventory += 1
            self.book.save()
            self.save()

    def is_active(self):
        return not self.actual_return_date

    @transaction.atomic
    def return_borrowing_with_fine(self, actual_return_date):
        self.return_book()

        if self.actual_return_date > self.expected_return_date:
            days_overdue = (
                actual_return_date - self.expected_return_date
            ).days
            fine_amount = days_overdue * self.book.daily_fee * FINE_MULT

            session_id = create_stripe_payment_session(
                borrowing=self,
                request=None
            )

            from payments.models import Payment
            Payment.objects.create(
                user=self.user,
                borrowing=self,
                amount=fine_amount,
                status="Pending",
                session_url=None,
                session_id=session_id,
            )

    def __str__(self):
        return f"{self.user} borrowed '{self.book.title}' on {self.borrow_date}"
