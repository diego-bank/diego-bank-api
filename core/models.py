"""
Models of the application
"""
import os
import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.utils import timezone

def user_image_field(instance, filename):
    """Generate file path for user image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'user', filename)

class Account(models.Model):
    """Conta para os clientes(usuários)"""
    agency = models.CharField(max_length=255)
    number = models.CharField(max_length=8, unique=True)
    balance = models.DecimalField(max_digits=5, decimal_places=2)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(default=timezone.now)
    

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
    # cnpj = models.CharField(max_length=14, unique=True)
    url_image = models.ImageField(null=True, upload_to=user_image_field)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'