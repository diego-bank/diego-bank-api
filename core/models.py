"""
Models of the application
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.utils import timezone


class UserManager (BaseUserManager):
    """Manager For users"""
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must be an email address")
        
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        
        return user
    
    def create_superuser(self, email, password):
        """Create, save and return a superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        
        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    """User instance in our system"""
    email = models.EmailField(max_length=255, unique=True, null=False)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    cpf = models.CharField(max_length=11, unique=True)
    cnpj = models.CharField(max_length=14, unique=True)
    # url_imagem = models.ImageField(null=True, upload_to=user_image_field)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'