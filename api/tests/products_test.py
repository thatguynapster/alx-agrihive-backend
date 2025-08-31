from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Category, Product


class ProductApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )
        self.farmer_user = User.objects.create_user(
            email="farmer@example.com", password="farmerpass123", role="farmer"
        )
        self.buyer_user = User.objects.create_user(
            email="buyer@example.com", password="buyerpass123", role="buyer"
        )
        self.category = Category.objects.create(
            name="Fruits", description="Fresh fruits"
        )
        self.product = Product.objects.create(
            name="Bananas",
            description="Yellow ripe bananas",
            price=10.50,
            quantity=20,
            unit="kg",
            farmer=self.farmer_user,
            category=self.category,
        )

    def test_list_products_public(self):
        url = reverse("product-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)

    def test_create_product_farmer_only(self):
        url = reverse("product-list")
        payload = {
            "name": "Apples",
            "description": "Red apples",
            "price": 15.00,
            "quantity": 10,
            "unit": "kg",
            "category": self.category.id,
        }

        # Buyer cannot create
        self.client.force_authenticate(user=self.buyer_user)
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Farmer can create
        self.client.force_authenticate(user=self.farmer_user)
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], "Apples")

    def test_update_product_owner_or_admin_only(self):
        url = reverse("product-detail", args=[self.product.id])
        payload = {"name": "Sweet Bananas"}

        # Buyer tries update → forbidden
        self.client.force_authenticate(user=self.buyer_user)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Farmer (owner) can update
        self.client.force_authenticate(user=self.farmer_user)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Sweet Bananas")

        # Admin can also update
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.patch(url, {"status": "sold"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "sold")

    def test_delete_product_owner_or_admin_only(self):
        url = reverse("product-detail", args=[self.product.id])

        # Buyer delete → forbidden
        self.client.force_authenticate(user=self.buyer_user)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Farmer delete → success
        self.client.force_authenticate(user=self.farmer_user)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
