from django.urls import path
from .views import (
    HealthCheckView,
    RegisterAPIView,
    LoginAPIView,
    UserListAPIView,
    UserDetailAPIView,
    CategoryDetailAPIView,
    CategoryListCreateAPIView,
    ProductListCreateAPIView,
    ProductDetailAPIView,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    # Authentication
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    # Users
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailAPIView.as_view(), name="user-detail"),
    # Categories
    path("categories/", CategoryListCreateAPIView.as_view(), name="category-list"),
    path(
        "categories/<int:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"
    ),
    # Products
    path("products/", ProductListCreateAPIView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),
]
