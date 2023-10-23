"""
Serializers of the user API.
"""
from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers

from django.utils.translation import gettext as _

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name', 'last_name', 'cpf', 'created_at', 'url_image']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 4},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
        }
        
        def create(self, validated_data):
            """Create and return a new user with encrypted password."""
            return get_user_model().objects.created_user(**validated_data)
        
        def updated(self, instance, validated_data):
            """Update and return user."""
            password = validated_data.pop('password', None)
            user = super().update(instance, validated_data)
            
            if password:
                user.set_password(password)
                user.save()
                
            return user