from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .permissions import IsAdminOrSelf
from .models import User


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
