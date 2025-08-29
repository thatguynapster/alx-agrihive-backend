from django.urls import reverse
from rest_framework.test import APITestCase


# Server health check test
class HealthCheckTests(APITestCase):
    def test_health_endpoint(self):
        url = reverse("health-check")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, {"status": "ok"})
