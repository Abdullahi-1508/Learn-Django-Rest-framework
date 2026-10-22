from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from library.models import Author, Book


class BookPermissionTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="Frank Herbert")
        cls.alice = User.objects.create_user(username="alice", password="pass")
        cls.bob = User.objects.create_user(username="bob", password="pass")
        cls.book_by_alice = Book.objects.create(
            title="Dune", author=cls.author, published_year=1965,
            created_by=cls.alice,
        )

    def test_anonymous_can_read_book(self):
        response = self.client.get(f'/api/books/{self.book_by_alice.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create_book(self):
        response = self.client.post('/api/books/', {
            'title': 'X', 'author_id': self.author.id, 'published_year': 2020,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bob_cannot_update_alice_book(self):
        self.client.force_authenticate(user=self.bob)
        response = self.client.put(f'/api/books/{self.book_by_alice.id}/', {
            'title': 'Hacked',
            'author_id': self.author.id,
            'published_year': 1965,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bob_cannot_delete_alice_book(self):
        self.client.force_authenticate(user=self.bob)
        response = self.client.delete(f'/api/books/{self.book_by_alice.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=self.book_by_alice.id).exists())

    def test_alice_can_delete_her_own_book(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.delete(f'/api/books/{self.book_by_alice.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book_by_alice.id).exists())

    def test_anonymous_cannot_create_book(self):
        """Anonymous users should get 401 when trying to create a book."""
        response = self.client.post('/api/books/', {
            'title': 'New Book',
            'author_id': self.author.id,
            'published_year': 2020,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.filter(title='New Book').count(), 0)