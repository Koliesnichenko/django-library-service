import os
import uuid

from django.db import models
from django.utils.text import slugify


def book_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/books/", filename)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=20,
        choices=[
            ("HARD", "Hard Cover"),
            ("SOFT", "Soft Cover"),
        ],
        default="SOFT",
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(decimal_places=2, max_digits=10)
    image = models.ImageField(null=True, blank=True, upload_to=book_image_path)

    class Meta:
        ordering = ["title"]
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.title} - {self.author}"
