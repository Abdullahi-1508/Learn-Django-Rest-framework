from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from library.models import Author, Book
from library.tests.base import BaseAPITestCase


class BookAPITestCase(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="Frank Herbert")
        cls.user = User.objects.create_user(username="alice", password="pass1234")
        cls.book = Book.objects.create(
            title="Dune", author=cls.author, published_year=1965,
            created_by=cls.user,
        )

    def test_list_books_anonymous(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_book_anonymous(self):
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Dune")

    def test_create_book_requires_auth(self):
        response = self.client.post('/api/books/', {
            'title': 'New Book',
            'author_id': self.author.id,
            'published_year': 2000,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/books/', {
            'title': 'New Book',
            'author_id': self.author.id,
            'published_year': 2000,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Book')
        # Verify created_by was set to the authenticated user
        new_book = Book.objects.get(title='New Book')
        self.assertEqual(new_book.created_by, self.user)

    def test_create_book_with_future_year_fails(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/books/', {
            'title': 'Future',
            'author_id': self.author.id,
            'published_year': 9999,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('published_year', response.data)

    def test_update_book_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(f'/api/books/{self.book.id}/', {
            'title': 'Dune (Revised)',
            'author_id': self.author.id,
            'published_year': 1965,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Dune (Revised)')

    def test_filter_books_by_author(self):
        """Filtering by author id should return only that author's books."""
        other_author = Author.objects.create(name="Isaac Asimov")
        Book.objects.create(
            title="Foundation",
            author=other_author,
            published_year=1951,
            created_by=self.user,
        )

        response = self.client.get(f'/api/books/?author={self.author.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Dune")
        self.assertEqual(response.data['results'][0]['author']['id'], self.author.id)
    def test_out_of_range_page_returns_404(self):
        """Requesting a page beyond the last should return 404."""
        # setUpTestData created 1 book; PAGE_SIZE is 5, so there's only 1 page.
        response = self.client.get('/api/books/?page=999')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Invalid page.")