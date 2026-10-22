from django.test import TestCase
from datetime import date
from library.models import Author, Book
from library.serializers import BookSerializer


class BookSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="Frank Herbert")
        cls.book = Book.objects.create(
            title="Dune", author=cls.author, published_year=1965,
        )

    def test_serialization_output(self):
        serializer = BookSerializer(self.book)
        data = serializer.data
        self.assertEqual(data['title'], "Dune")
        self.assertEqual(data['author']['name'], "Frank Herbert")
        self.assertNotIn('author_id', data)   # write_only, never in output

    def test_future_published_year_is_invalid(self):
        future_year = date.today().year + 10
        serializer = BookSerializer(data={
            'title': 'Future Book',
            'author_id': self.author.id,
            'published_year': future_year,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('published_year', serializer.errors)

    def test_duplicate_title_author_is_invalid(self):
        serializer = BookSerializer(data={
            'title': 'Dune',
            'author_id': self.author.id,
            'published_year': 1965,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_valid_data_passes(self):
        serializer = BookSerializer(data={
            'title': 'Dune Messiah',
            'author_id': self.author.id,
            'published_year': 1969,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['title'], 'Dune Messiah')
        self.assertEqual(serializer.validated_data['author'], self.author)