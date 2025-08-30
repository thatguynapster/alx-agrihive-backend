from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Public representation of a user (safe fields)"""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "name",
            "phone_number",
            "address",
            "role",
            "created_at",
            "updated_at",
        )


class RegisterSerializer(serializers.ModelSerializer):
    """Used for registration. password is write_only."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "password", "name", "phone_number", "address", "role")

    def create(self, validated_data):
        # Use the custom manager to create the user and hash the password
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Expect email + password for login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError('Must include "email" and "password".')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs
