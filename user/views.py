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
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from api import serializers
import random, decimal
from core.models import Account

class CreateUserAPIView(generics.CreateAPIView):
    """Create a new user"""
    serializer_class = UserSerializer
    # permission_classes = [AllowAny, ]
    
    def create(self, request, *args, **kwargs):
        print(request.data)
        user_serializer = self.get_serializer(data=request.data)
        print(user_serializer)
        print("\n\n")
        print(user_serializer.is_valid())
        print("\n\n")
        
        if user_serializer.is_valid():
            
            user = user_serializer.save()
            
            print(user)
            
            data_account = {}
            serializer_account = serializers.AccountSerializer(data=data_account)
            
            if serializer_account.is_valid():
                agency = '0001'
                number = ''
                for n in range(8):
                    number += str(random.randint(0, 9))
                
                account = Account(
                    user=user,
                    agency=agency,
                    number=number,
                )
                
                account.balance = decimal.Decimal(0)
                
                account.save()
                
                return Response({'message': 'Created'}, status=status.HTTP_201_CREATED)

        return Response({"Erro": "Erro"}, status=status.HTTP_400_BAD_REQUEST)
            

class ManagerUserAPIView(generics.RetrieveUpdateAPIView):
    """Manage for the users"""
    serializer_class = UserSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Retrieve and return a user."""
        return self.request.user
    
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to user."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)