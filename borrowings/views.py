from datetime import date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    ReturnBorrowingSerializer
)
from lib_bot.bot import send_telegram_message
from payments.utils import create_stripe_payment_session


@extend_schema(tags=["borrowings"])
@extend_schema_view(
    list=extend_schema(
        description="List of all borrowings "
                    "filtered by 'is_active' or 'user_id'.",
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="Filter borrowings by user_id",
                required=False,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name="is_active",
                description="Filter borrowings by status ('true' or 'false').",
                required=False,
                type=OpenApiTypes.BOOL,
            ),
        ],
        responses={status.HTTP_200_OK: BorrowingSerializer()},
    ),
    retrieve=extend_schema(
        summary="Retrieve all borrowings by ID.",
        description="Retrieve all borrowings by ID.",
        responses={status.HTTP_200_OK: BorrowingSerializer()},
    ),
    create=extend_schema(
        summary="Create a new borrowing",
        description="Create a new borrowing.",
        responses={status.HTTP_201_CREATED: BorrowingSerializer()},
    ),
)
class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("user", "book").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "retrieve":
            return BorrowingSerializer
        if self.action == "return_borrowing":
            return ReturnBorrowingSerializer
        return BorrowingSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        if user.is_staff and user_id:
            queryset = queryset.filter(user__id=user_id)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_staff:
            serializer.validated_data["user"] = user

        borrowing = serializer.save()

        create_stripe_payment_session(borrowing, self.request)

        message = (
            f"<b> New Borrowing</b>\n"
            f"User: {borrowing.user.email}\n"
            f"Book: {borrowing.book.title}\n"
            f"Borrowed: {borrowing.borrow_date}\n"
            f"Return by: {borrowing.expected_return_date}\n"
        )
        send_telegram_message(message)

    @extend_schema(
        summary="Return a borrowed book by ID.",
        description="Set actual_return_date to today and increase book inventory. "
                "Raises error if already returned.",
        responses={status.HTTP_200_OK: BorrowingSerializer()},
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated],
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        user = request.user

        if borrowing.user != user and not user.is_staff:
            return Response(
                {"error": "You can return only your own borrowings."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if borrowing.actual_return_date:
            return Response(
                {"error": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.return_borrowing_with_fine(actual_return_date=date.today())

        message = (
            f"<b>Book Returned</b>\n"
            f"User: {borrowing.user.email}\n"
            f"Book: {borrowing.book.title}\n"
            f"Borrowed: {borrowing.borrow_date}\n"
            f"Returned: {borrowing.actual_return_date}"
        )
        send_telegram_message(message)

        return Response(
            {"detail": "Borrowing successfully returned."},
            status=status.HTTP_200_OK,
        )
