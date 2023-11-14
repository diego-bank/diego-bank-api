from rest_framework import (
    viewsets,
    status
)
from rest_framework.generics import mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt import authentication as authenticationJWT
from core.models import Account, Transaction, Card
from api import serializers
import random, decimal

from rest_framework.decorators import action

# class AccountSearchViewSet(mixins.ListModelMixin):
#     queryset = Account.objects.all()
#     authentication_classes = [authenticationJWT.JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer = serializers.AccountSerializer
    
#     def get_queryset(self, request):
#         number = request.query_params.get('number', None)
#         return Account.objects.filter(number=number).order_by("-created_at").first()
    
class AccountSearchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = serializers.AccountSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self, request):
        number = request.data.get('number', None)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        print(number)
        return Account.objects.filter(number=number).order_by("-created_at").first()

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Pegar contas para usuários autenticados"""
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by("-created_at").distinct()
        
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'create':
            return serializers.AccountDetailSerializer
        
        return serializers.AccountSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = serializers.AccountSerializer(data=request.data)
        if serializer.is_valid():
            agency = '0001'
            number = ''
            for n in range(8):
                number += str(random.randint(0, 9))
                
            account = Account(
                user=self.request.user,
                agency=agency,
                number=number,
            )
            
            account.balance = decimal.Decimal(0)
            
            account.save()
            return Response({'message': 'Created', 'agency': account.agency, 'number': account.number}, status=status.HTTP_201_CREATED)
    
    @action(methods=['POST'], detail=True, url_path='withdraw')
    def withdraw(self, request, pk=None):
        account = Account.objects.filter(id=pk).first()
        
        serializer_received = serializers.WithdrawSerializer(data=request.data)
        
        if serializer_received.is_valid() and account:
            value_withdraw = decimal.Decimal(serializer_received.validated_data.get('value'))
            balance = decimal.Decimal(account.balance)
            
            comparison = balance.compare(value_withdraw)
            
            if comparison == 0 or comparison == 1:
                new_value = 0 if balance - value_withdraw < 0 else balance - value_withdraw
                
                account.balance = new_value
                
                account.save()
                
                transaction_data = {
                    'sender': account.id,
                    'value': value_withdraw,
                    'description': 'Withdraw'
                }
                
                transaction_serializer = serializers.TransactionWithdrawSerializer(data=transaction_data)
                
                if transaction_serializer.is_valid():
                    transaction_serializer.save()
                
                return Response({"saldo": account.balance}, status=status.HTTP_200_OK)
            
            return Response({'message': "Saldo insuficiente"}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializer_received.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True, url_path='deposit')
    def deposit(self, request, pk=None):
        account = Account.objects.filter(id=pk).first()
        
        serializer_received = serializers.DepositSerializer(data=request.data)
        
        if serializer_received.is_valid() and account:
            balance = decimal.Decimal(account.balance)
            value_deposit = decimal.Decimal(serializer_received.validated_data.get('value'))
            
            account.balance = balance + value_deposit
            account.save()
            
            transaction_data = {
                    'recipient': account.id,
                    'value': value_deposit,
                    'description': 'Deposit'
                }
                
            transaction_serializer = serializers.TransactionDepositSerializer(data=transaction_data)
            
            if transaction_serializer.is_valid():
                transaction_serializer.save()
            
            return Response({"saldo": account.balance}, status=status.HTTP_200_OK)
            
        return Response(serializer_received.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TransactionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = serializers.TransactionSerializer(data=request.data)
        sender = Account.objects.all().filter(user=self.request.user).order_by("-created_at").distinct().first()
        
        print(serializer.initial_data["value"])
        
        data = {
            "value": serializer.initial_data["value"],
            "description": serializer.initial_data["description"],
            "recipient": serializer.initial_data["recipient"],
            "sender": sender.pk
        }
        
        serializerFinal = serializers.TransactionSerializer(data=data)
        
        if serializerFinal.is_valid():
            sender.balance -= serializerFinal.validated_data.get('value')
            recipient = serializerFinal.validated_data.get('recipient')
            recipient.balance += serializerFinal.validated_data.get('value')
            
            sender.save()
            recipient.save()
            
            serializerFinal.save()
            
            return Response({"saldo": sender.balance}, status=status.HTTP_200_OK)
        else:
            return Response(serializerFinal.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        """Pegar contas para usuários autenticados"""
        queryset = self.queryset
        result1 = queryset.filter(
            sender=Account.objects.all().filter(user=self.request.user).order_by("-created_at").distinct().first()
        ).order_by("-created_at").distinct()
        result2 = queryset.filter(
            recipient=Account.objects.all().filter(user=self.request.user).order_by("-created_at").distinct().first()
        ).order_by("-created_at").distinct()
        
        
        return result1.union(result2, all=True).order_by("-created_at")
    
    
class CardViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Card.objects.all()
    serializer_class = serializers.CardSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    