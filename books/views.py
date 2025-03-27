from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, mixins, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from books.filters import BookFilter
from books.models import Book
from books.serializers import BookSerializer, BookImageSerializer


@extend_schema(tags=["book"])
@extend_schema_view(
    list=extend_schema(
        summary="List of all books.",
        description="List of  all books.",
        responses={status.HTTP_200_OK: BookSerializer()},
    ),
    retrieve=extend_schema(
        summary="Retrieve a book by ID.",
        description="Retrieve a book by ID.",
        responses={status.HTTP_200_OK: BookSerializer()},
    ),
    create=extend_schema(
        summary="Create a new book.",
        description="Create a new book.",
        responses={status.HTTP_200_OK: BookSerializer()},
    ),
    update=extend_schema(
        summary="Update a book.",
        description="Update a book.",
        responses={status.HTTP_200_OK: BookSerializer()},
    ),
    partial_update=extend_schema(
        summary="Partially update a book.",
        description="Partially update a book.",
        responses={status.HTTP_200_OK: BookSerializer()},
    ),
    destroy=extend_schema(
        summary="Delete a book.",
        description="Delete a book.",
        responses={status.HTTP_200_OK: BookSerializer()},
    )
)
class BookViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "author"]
    filterset_class = BookFilter
    ordering_fields = ["id", "title", "author", "inventory", "daily_fee"]
    ordering = ["id"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == "upload_image":
            return BookImageSerializer

        return BookSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        book = self.get_object()
        serializer = self.get_serializer(book, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
