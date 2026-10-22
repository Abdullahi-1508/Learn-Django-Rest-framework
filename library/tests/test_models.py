from django.test import TestCase
from library.models import Author, Book


class AuthorModelTest(TestCase):
    def test_author_str_returns_name(self):
        author = Author.objects.create(name="Frank Herbert")
        self.assertEqual(str(author), "Frank Herbert")


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="Frank Herbert")

    def test_book_str_returns_title(self):
        book = Book.objects.create(
            title="Dune", author=self.author, published_year=1965,
        )
        self.assertEqual(str(book), "Dune")

    def test_books_related_name(self):
        book1 = Book.objects.create(title="Dune", author=self.author, published_year=1965)
        book2 = Book.objects.create(title="Dune Messiah", author=self.author, published_year=1969)
        self.assertEqual(self.author.books.count(), 2)
        self.assertIn(book1, self.author.books.all())
        self.assertIn(book2, self.author.books.all())

    def test_unique_title_per_author_constraint(self):
        Book.objects.create(title="Dune", author=self.author, published_year=1965)
        with self.assertRaises(Exception):   # IntegrityError under the hood
            Book.objects.create(title="Dune", author=self.author, published_year=1965)