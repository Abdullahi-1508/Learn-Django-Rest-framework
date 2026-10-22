import tempfile
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from library.models import Author, Book


def make_test_image(name='test.jpg', size=(100, 100)):
    """Create a small image in memory for upload tests."""
    file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    image = Image.new('RGB', size, color='red')
    image.save(file, format='JPEG')
    file.seek(0)
    content = file.read()
    file.close()
    return SimpleUploadedFile(name, content, content_type='image/jpeg')


class BookUploadTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="Frank Herbert")
        cls.user = User.objects.create_user(username="alice", password="pass")

    def test_upload_cover_image(self):
        """Uploading a valid image should create a book with a cover URL."""
        self.client.force_authenticate(user=self.user)
        image = make_test_image()

        response = self.client.post('/api/books/', {
            'title': 'Dune',
            'author_id': self.author.id,
            'published_year': 1965,
            'cover': image,
        }, format='multipart')   # ← multipart for file uploads

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('cover', response.data)
        self.assertIsNotNone(response.data['cover'])
        self.assertTrue(response.data['cover'].endswith('.jpg'))

    def test_upload_non_image_fails(self):
        """Uploading a non-image file should fail."""
        self.client.force_authenticate(user=self.user)
        fake = SimpleUploadedFile('test.txt', b'not an image', content_type='text/plain')

        response = self.client.post('/api/books/', {
            'title': 'Dune',
            'author_id': self.author.id,
            'published_year': 1965,
            'cover': fake,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cover', response.data)