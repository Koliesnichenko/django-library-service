import stripe
from django.conf import settings
from django.db import transaction
from payments.models import Payment
stripe.api_key = settings.STRIPE_SECRET_KEY


@transaction.atomic
def create_stripe_payment_session(borrowing, request):
    days_of_borrowing = (
        borrowing.expected_return_date - borrowing.borrow_date
    ).days

    total_amount = borrowing.book.daily_fee * days_of_borrowing

    try:

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Book borrowing - {borrowing.book.title}",
                        },
                        "unit_amount": int(total_amount * 100),
                    },
                    "quantity": 1,
                }],
            mode="payment",
            success_url=f"http://127.0.0.1:8000/api/payments/success/"
                        f"?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url="http://127.0.0.1:8000/api/payments/cancel/",
        )
        payment = Payment.objects.create(
            user=borrowing.user,
            borrowing=borrowing,
            amount=total_amount,
            status="Pending",
            session_id=session.id,
            session_url=session.url,
        )
        return payment, session

    except stripe.error.StripeError as e:
        print(f"Stripe Error: {e}")
        raise e
