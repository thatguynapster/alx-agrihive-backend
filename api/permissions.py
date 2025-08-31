from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrSelf(BasePermission):
    """
    - Read (GET) and update (PUT/PATCH) allowed for:
        * admin users (is_staff) OR the object owner (user == request.user)
    - Delete only allowed for admin users.
    """

    def has_object_permission(self, request, view, obj):
        # admins can do anything
        if request.user and request.user.is_staff:
            return True

        # SAFE_METHODS are GET, HEAD, OPTIONS -> allow if it's the owner
        if request.method in SAFE_METHODS:
            return obj == request.user

        # allow updates by owner
        if request.method in ("PUT", "PATCH"):
            return obj == request.user

        # all other methods (DELETE etc.) are false unless admin
        return False


class IsFarmerOrAdminOwner(BasePermission):
    """
    - SAFE_METHODS (GET, HEAD, OPTIONS): allowed for anyone
    - Create: only users with role='farmer' or admins
    - Update/Delete: only product owner (farmer) or admin
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role == "farmer" or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            obj.farmer == request.user or request.user.is_staff
        )
