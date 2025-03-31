from django.urls import path

from payments.views import (
    PaymentListCreateView,
    PaymentDetailView,
    PaymentCancelView,
    PaymentSuccessView
)

urlpatterns = [
    path("", PaymentListCreateView.as_view(), name="payment_list"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]
