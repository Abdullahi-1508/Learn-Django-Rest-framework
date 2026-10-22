from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache
from library.tests.base import BaseAPITestCase



class ThrottleTest(BaseAPITestCase):
    def test_anon_throttle_limits_requests(self):
        """Anonymous requests should be throttled after 10 per minute."""
        cache.clear()

        # settings say anon: '10/min'
        for i in range(10):
            response = self.client.get('/api/books/')
            self.assertEqual(
                response.status_code, status.HTTP_200_OK,
                f"Request {i+1} failed: {response.status_code} {response.data}"
            )

        response = self.client.get('/api/books/')
        self.assertEqual(
            response.status_code, status.HTTP_429_TOO_MANY_REQUESTS,
            f"Request 11 should be throttled: got {response.status_code} {response.data}"
        )