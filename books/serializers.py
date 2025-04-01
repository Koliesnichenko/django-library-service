from rest_framework import serializers

from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee", "image")

    def get_download_link(self, obj):
        if obj.image:
            return self.context["request"].build_absolute_uri(obj.image.url)
        return None


class BookImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "image")
