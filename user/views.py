"""
Views for the user API.
"""
from rest_framework.response import Response
from rest_framework import (
    status,
    generics
)
from rest_framework_simplejwt import authentication as authenticationJWT

from user.serializers import UserSerializer
from user.permissions import IsCreationOrIsAuthenticated

from rest_framework.permissions import IsAuthenticated

class CreateUserAPIView(generics.CreateAPIView):
    """Create a new user"""
    serializer_class = UserSerializer

class ManagerUserAPIView(generics.RetrieveUpdateAPIView):
    """Manage for the users"""
    serializer_class = UserSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def get_object(self):
        """Retrieve and return a user."""
        return self.request.user