from django.core.cache import cache
from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):
    """Base class for API tests. Clears the throttle cache before each test."""
    def setUp(self):
        cache.clear()