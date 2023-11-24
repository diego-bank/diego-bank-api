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
from datetime import date, timedelta
from random import randint

from cpf_field.models import CPFField

def user_image_field(instance, filename):
    """Generate file path for user image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'user', filename)

class Account(models.Model):
    """Conta para os clientes(usuários)"""
    agency = models.CharField(max_length=255)
    number = models.CharField(max_length=8, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self) -> str:
        return f'{self.agency} - {self.number}'
    

class UserManager(BaseUserManager):
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
    cpf =CPFField('cpf', unique=True)
    # cnpj = models.CharField(max_length=14, unique=True)
    url_image = models.ImageField(default=None, null=True, upload_to=user_image_field)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'
    
class Address(models.Model):
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    number = models.PositiveIntegerField()
    complement = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=255)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING
    )
    
class Card(models.Model):
    number = models.CharField(max_length=20)
    cvv = models.CharField(max_length=3)
    expiration_date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.number = f"{randint(1000,9999)} {randint(1000,9999)} {randint(1000,9999)} {randint(1000,9999)}"
        self.cvv = f"{randint(100,999)}"
        self.expiration_date = date.today() + timedelta(3650)

        super(Card, self).save(*args, **kwargs)
        
    def __str__(self) -> str:
        return self.number
    
class Transaction(models.Model):
    value = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    recipient = models.ForeignKey(Account, on_delete=models.DO_NOTHING, related_name="recipient", null=True)
    card = models.ForeignKey(Card, on_delete=models.DO_NOTHING, related_name="card", null=True)
    sender = models.ForeignKey(Account, on_delete=models.DO_NOTHING, related_name="sender", null=True)

class Loan(models.Model):
    value = models.DecimalField(decimal_places=2, max_digits=10)
    date = models.DateTimeField(auto_now_add=True)
    payments = models.IntegerField()
    approved = models.BooleanField(default=False)
    payed = models.BooleanField(default=False)
    account = models.ForeignKey(Account, related_name="Loan", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
class LoanPayment(models.Model):
    value = models.DecimalField(decimal_places=2, max_digits=10)
    payment_date = models.DateTimeField(auto_now_add=True)
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)