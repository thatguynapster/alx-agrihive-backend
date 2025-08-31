from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    CategorySerializer,
)
from .models import User, Category, Product, Order
from .permissions import IsFarmerOrAdminOwner
from .serializers import ProductSerializer
from .serializers import OrderSerializer
from .permissions import IsBuyerOrAdmin
from .permissions import IsAdminOrSelf


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    """
    POST /api/auth/register/
    - Create a new user (farmer/buyer/transporter)
    - Returns token + user object
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    """
    POST /api/auth/login/
    - Returns token + user object for valid credentials
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class UserListAPIView(generics.ListAPIView):
    """
    GET /api/users/  -- admin only
    """

    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET / PUT / DELETE /api/users/{id}/
    - GET: admin or owner
    - PUT/PATCH: admin or owner
    - DELETE: admin only (permission class ensures this)
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSelf]


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/categories/  -> list all categories (public)
    POST /api/categories/ -> create new category (admin only)
    """

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/categories/<id>/  -> public
    PUT/PATCH/DELETE -> admin only
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]


class ProductListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/products/ -> public list
    POST /api/products/ -> only farmers or admin
    """

    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [IsFarmerOrAdminOwner]

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/products/<id>/ -> public
    PUT/PATCH/DELETE -> only product owner (farmer) or admin
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsFarmerOrAdminOwner]


class OrderListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/orders/ -> buyer sees their orders, admin sees all
    POST /api/orders/ -> buyer only
    """

    serializer_class = OrderSerializer
    permission_classes = [IsBuyerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by("-created_at")
        return Order.objects.filter(buyer=user).order_by("-created_at")


class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/orders/<id>/ -> buyer sees own, admin sees all
    PUT/PATCH -> admin can update status, buyer cannot
    DELETE -> admin only
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsBuyerOrAdmin]

    def update(self, request, *args, **kwargs):
        # only admins can update order status/delivery_date
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update orders."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # only admins can delete
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete orders."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
