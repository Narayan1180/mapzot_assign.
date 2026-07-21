# products/permissions.py

from rest_framework.permissions import BasePermission


class ProductPermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        role = request.user.role
        print(role)
        # Type 1 -> Read, Update, Delete
        if role == "type1":
            return request.method in ["GET", "PUT", "PATCH", "DELETE"]

        # Type 2 -> Read, Create, Update
        elif role == "type2":
            return request.method in ["GET", "POST", "PUT", "PATCH"]

        # Type 3 -> Read, Create
        elif role == "type3":
            return request.method in ["GET", "POST"]

        return False