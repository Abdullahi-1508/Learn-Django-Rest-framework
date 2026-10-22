from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission. Read access for anyone.
    Write access only for the object's creator (`created_by`).
    """
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS are safe — allow them.
        if request.method in SAFE_METHODS:
            return True
        # For write methods, require the object to be owned by the current user.
        return obj.created_by == request.user