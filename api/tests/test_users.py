from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import User


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123", name="Admin User"
        )
        # Create a normal buyer user
        self.buyer_user = User.objects.create_user(
            email="buyer@example.com",
            password="buyerpass123",
            name="Buyer User",
            role="buyer",
        )

    def test_register_user(self):
        """New user should be able to register and get token"""
        url = reverse("auth-register")
        payload = {
            "email": "newuser@example.com",
            "password": "strongpass123",
            "name": "New User",
            "role": "farmer",
        }
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["user"]["email"], payload["email"])
        self.assertTrue(User.objects.filter(email=payload["email"]).exists())

    def test_login_user(self):
        """Existing user can login with correct credentials"""
        url = reverse("auth-login")
        payload = {"email": "buyer@example.com", "password": "buyerpass123"}
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["user"]["email"], "buyer@example.com")

    def test_login_invalid_credentials(self):
        """Login fails with wrong password"""
        url = reverse("auth-login")
        payload = {"email": "buyer@example.com", "password": "wrongpass"}
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)


class UserPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create users
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123", name="Admin User"
        )
        self.buyer_user = User.objects.create_user(
            email="buyer@example.com",
            password="buyerpass123",
            name="Buyer User",
            role="buyer",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="otherpass123",
            name="Other User",
            role="buyer",
        )

    def test_user_list_admin_only(self):
        """Only admin can view user list"""
        url = reverse("user-list")

        # not logged in → 401
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged in as buyer → 403
        self.client.force_authenticate(user=self.buyer_user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # logged in as admin → 200
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 2)

    def test_user_detail_self_or_admin(self):
        """User can see their own detail, not others; admin can see all"""
        url = reverse("user-detail", args=[self.buyer_user.id])

        # Buyer fetching own detail → 200
        self.client.force_authenticate(user=self.buyer_user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Buyer trying to fetch OTHER user detail → 403
        url_other = reverse("user-detail", args=[self.other_user.id])
        res = self.client.get(url_other)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin fetching other user detail → 200
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(url_other)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_delete_admin_only(self):
        """Delete allowed only for admin"""
        url = reverse("user-detail", args=[self.other_user.id])

        # Buyer trying delete → 403
        self.client.force_authenticate(user=self.buyer_user)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin delete → 204
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.other_user.id).exists())
