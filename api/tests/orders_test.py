from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import User, Category, Product, Order


class OrderAPITests(APITestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(
            name="Admin",
            email="admin@test.com",
            password="adminpass",
            role="admin",
            is_staff=True,
        )
        self.buyer = User.objects.create_user(
            name="Buyer", email="buyer@test.com", password="buyerpass", role="buyer"
        )
        self.other_buyer = User.objects.create_user(
            name="Other Buyer",
            email="other@test.com",
            password="otherpass",
            role="buyer",
        )
        self.farmer = User.objects.create_user(
            name="Farmer", email="farmer@test.com", password="farmerpass", role="farmer"
        )

        # Category & Product
        self.category = Category.objects.create(
            name="Fruits", description="Fresh fruits"
        )
        self.product = Product.objects.create(
            name="Bananas",
            description="Fresh bananas",
            price=10.5,
            quantity=20,
            unit="kg",
            category=self.category,
            farmer=self.farmer,
        )

        # Tokens
        login_admin = self.client.post(
            reverse("auth-login"), {"email": "admin@test.com", "password": "adminpass"}
        )
        self.admin_token = login_admin.data["token"]

        login_buyer = self.client.post(
            reverse("auth-login"), {"email": "buyer@test.com", "password": "buyerpass"}
        )
        self.buyer_token = login_buyer.data["token"]

        login_other = self.client.post(
            reverse("auth-login"), {"email": "other@test.com", "password": "otherpass"}
        )
        self.other_buyer_token = login_other.data["token"]

    def test_buyer_can_create_order(self):
        url = reverse("order-list")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.buyer_token}")
        response = self.client.post(
            url, {"product": self.product.id, "quantity": 2}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 2)
        self.assertEqual(float(response.data["total_price"]), 21.0)

    def test_farmer_cannot_create_order(self):
        # login farmer
        login_farmer = self.client.post(
            reverse("auth-login"),
            {"email": "farmer@test.com", "password": "farmerpass"},
        )
        farmer_token = login_farmer.data["token"]

        url = reverse("order-list")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {farmer_token}")
        response = self.client.post(
            url, {"product": self.product.id, "quantity": 2}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_buyer_can_view_own_orders_but_not_others(self):
        # Buyer places order
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.buyer_token}")
        order_response = self.client.post(
            reverse("order-list"),
            {"product": self.product.id, "quantity": 1},
            format="json",
        )
        order_id = order_response.data["id"]

        # Same buyer can retrieve it
        response = self.client.get(reverse("order-detail", args=[order_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["buyer"], self.buyer.id)

        # Other buyer tries to access it
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.other_buyer_token}")
        response = self.client.get(reverse("order-detail", args=[order_id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_all_orders(self):
        # Buyer creates order
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.buyer_token}")
        self.client.post(
            reverse("order-list"),
            {"product": self.product.id, "quantity": 3},
            format="json",
        )

        # Admin can list all
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_admin_can_update_order_status(self):
        # Buyer creates order
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.buyer_token}")
        order_response = self.client.post(
            reverse("order-list"),
            {"product": self.product.id, "quantity": 2},
            format="json",
        )
        order_id = order_response.data["id"]

        # Admin updates status
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.patch(
            reverse("order-detail", args=[order_id]),
            {"status": "confirmed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "confirmed")

    def test_buyer_cannot_update_or_delete_order(self):
        # Buyer creates order
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.buyer_token}")
        order_response = self.client.post(
            reverse("order-list"),
            {"product": self.product.id, "quantity": 1},
            format="json",
        )
        order_id = order_response.data["id"]

        # Buyer tries update
        response = self.client.patch(
            reverse("order-detail", args=[order_id]),
            {"status": "cancelled"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Buyer tries delete
        response = self.client.delete(reverse("order-detail", args=[order_id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_order(self):
        # Buyer creates order
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.buyer_token}")
        order_response = self.client.post(
            reverse("order-list"),
            {"product": self.product.id, "quantity": 1},
            format="json",
        )
        order_id = order_response.data["id"]

        # Admin deletes it
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.delete(reverse("order-detail", args=[order_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order_id).exists())
