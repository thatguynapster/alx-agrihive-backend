from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser (admin)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model:
        - uses email as unique identifier (LOGIN)
        - fields from your ERD plus created_at & updated_at
    """

    ROLE_FARMER = "farmer"
    ROLE_BUYER = "buyer"
    ROLE_TRANSPORTER = "transporter"

    ROLE_CHOICES = [
        (ROLE_FARMER, "Farmer"),
        (ROLE_BUYER, "Buyer"),
        (ROLE_TRANSPORTER, "Transporter"),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)

    # permissions
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email is required by USERNAME_FIELD

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("sold", "Sold"),
        ("inactive", "Inactive"),
    ]

    farmer = models.ForeignKey(
        "User", on_delete=models.PROTECT, related_name="products"
    )
    category = models.ForeignKey(
        "Category", on_delete=models.PROTECT, related_name="products"
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)  # e.g., kg, liters

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.farmer.email})"
