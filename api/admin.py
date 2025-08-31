from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "name", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "name")

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name", "phone_number", "address", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "name", "role"),
            },
        ),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "farmer",
        "category",
        "price",
        "quantity",
        "unit",
        "status",
    )
    list_filter = ("status", "category")
    search_fields = ("name", "farmer__email")
    readonly_fields = ("created_at", "updated_at")


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "buyer",
        "product",
        "quantity",
        "total_price",
        "status",
        "delivery_date",
    )
    list_filter = ("status",)
    search_fields = ("buyer__email", "product__name")
    readonly_fields = (
        "created_at",
        "updated_at",
    )
