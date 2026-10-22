from django.db import models
from django.contrib.auth.models import User
# For the validations
from django.core.validators import MinValueValidator, MaxValueValidator



class Author(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    # This is where we validate
    published_year = models.IntegerField(validators=[MinValueValidator(1450), MaxValueValidator(9999)])

    # To add the images
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_books'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # This will not let a user add a book that has already existed in the db with same author
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title","author"],
                name="unique_title_per_author"
            ),
        ]

    def __str__(self):
        return self.title

