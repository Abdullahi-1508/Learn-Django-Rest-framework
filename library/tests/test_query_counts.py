from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from library.models import Author, Book
from library.tests.base import BaseAPITestCase


class QueryCountTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(name="Frank Herbert")
        user = User.objects.create_user(username="alice", password="pass")
        for i in range(5):
            Book.objects.create(
                title=f"Book {i}",
                author=author,
                published_year=1965 + i,
                created_by=user,
            )

    def test_book_list_query_count(self):
        """The book list endpoint should use exactly 2 queries."""
        client = APIClient()
        with self.assertNumQueries(2):
            response = client.get('/api/books/')
        self.assertEqual(response.status_code, 200)

    def test_author_list_query_count(self):
        """The author list endpoint should use exactly 3 queries."""
        client = APIClient()
        with self.assertNumQueries(3):
            response = client.get('/api/authors/')
        self.assertEqual(response.status_code, 200)