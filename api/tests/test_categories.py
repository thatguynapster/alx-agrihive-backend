from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Category


class CategoryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )
        self.buyer_user = User.objects.create_user(
            email="buyer@example.com", password="buyerpass123", role="buyer"
        )
        self.category = Category.objects.create(
            name="Fruits", description="All fresh fruits"
        )

    def test_list_categories_public(self):
        url = reverse("category-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)

    def test_retrieve_category_public(self):
        url = reverse("category-detail", args=[self.category.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Fruits")

    def test_create_category_admin_only(self):
        url = reverse("category-list")
        payload = {"name": "Vegetables", "description": "Fresh veggies"}

        # non-authenticated → 401
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # authenticated non-admin → 403
        self.client.force_authenticate(user=self.buyer_user)
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # admin → success
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], payload["name"])

    def test_update_delete_admin_only(self):
        url = reverse("category-detail", args=[self.category.id])
        payload = {"name": "Updated Fruits"}

        # non-admin update → 403
        self.client.force_authenticate(user=self.buyer_user)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # admin update → 200
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Updated Fruits")

        # admin delete → 204
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
