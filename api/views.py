from rest_framework import (
    viewsets,
    status,
    generics
)
from rest_framework.generics import mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt import authentication as authenticationJWT
from core.models import Account, Transaction, Card, Loan
from api import serializers
import random, decimal

from rest_framework.decorators import action


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_action_classes = {
        'deposit': serializers.DepositSerializer,
        'withdraw': serializers.WithdrawSerializer
    }
    
    def get_queryset(self):
        """Pegar contas para usuários autenticados"""
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by("created_at").distinct()
        
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
    
    @action(methods=['GET'], detail=False, url_path='search/(?P<number>[^/.]+)')
    def get_account_by_number(self, request, pk=None, number=None):
        try:
            account = Account.objects.filter(number=number).order_by("created_at").first()
            serializer = serializers.AccountSerializer(account)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['POST'], detail=False, url_path='withdraw', serializer_class = serializers.WithdrawSerializer)
    def withdraw(self, request):
        account = Account.objects.all().filter(user=self.request.user).order_by("created_at").distinct().first()
        
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
    
    @action(methods=['POST'], detail=False, url_path='deposit', serializer_class = serializers.DepositSerializer)
    def deposit(self, request):
        account = Account.objects.all().filter(user=self.request.user).order_by("created_at").distinct().first()
        
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
    
class TransactionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_action_classes = {
        'card': serializers.TransactionSerializer,
    }
    
    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = serializers.CreateTransactionSerializer(data=request.data)
        sender = Account.objects.all().filter(user=self.request.user).order_by("created_at").distinct().first()
        
        try:
            card = serializer.initial_data["card"]
        except:
            card = None
            
        data = {
            "value": serializer.initial_data["value"],
            "description": serializer.initial_data["description"],
            "recipient": serializer.initial_data["recipient"],
            "card": card,
            "sender": sender.pk
        }
        
        print(data)
        
        serializerFinal = serializers.CreateTransactionSerializer(data=data)
        
        if serializerFinal.is_valid():
            
            if (sender.balance - serializerFinal.validated_data.get('value')) > 0:
                
                if (serializerFinal.validated_data.get('card') == None):
                    print(sender.balance)
                    sender.balance -= serializerFinal.validated_data.get('value')
                    recipient = serializerFinal.validated_data.get('recipient')
                    print(recipient)
                    recipient.balance += serializerFinal.validated_data.get('value')
                    print(recipient.balance)
                    
                    sender.save()
                    recipient.save()
                    
                serializerFinal.save()
                
                return Response({"Valor Enviado": serializerFinal.validated_data.get('value')}, status=status.HTTP_200_OK)
            else:
                return Response({"Erro":"Saldo Insuficiente"}, status=status.HTTP_200_OK)
        else:
            return Response(serializerFinal.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        """Pegar contas para usuários autenticados"""
        queryset = self.queryset
        result1 = queryset.filter(
            sender=Account.objects.all().filter(user=self.request.user).order_by("created_at").distinct().first()
        ).exclude(card__isnull=False).order_by("-created_at").distinct()
        result2 = queryset.filter(
            recipient=Account.objects.all().filter(user=self.request.user).order_by("created_at").distinct().first()
        ).order_by("-created_at").distinct()
        
        
        return result1.union(result2, all=True).order_by("-created_at")
    
    @action(methods=['GET'], detail=False, url_path='card', serializer_class=serializers.TransactionSerializer)
    def cards(self, request):
        queryset = self.queryset
        result = queryset.filter(
            sender=Account.objects.all().filter(user=self.request.user).order_by("created_at").distinct().first()
        ).exclude(card__isnull=True).order_by("-created_at").distinct()
        
        serializer = serializers.TransactionSerializer(result, many=True)

        return Response(serializer.data)
    
    # def retrieve(self, *args, **kwargs):
    #     queryset = self.queryset
    #     if Account.objects.all().filter(pk=self.request.pk, sender=self.request.user) or Account.objects.all().filter(pk=self.request.pk, recipient=self.request.user):
    #         return Account.objects.all().filter(pk=self.request.pk)
    #     else: 
    #         return Response({"ERRO": "Essa não é uma transação válida para esse usuário"}, status=status.HTTP_400_BAD_REQUEST)
    
    
class CardViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Card.objects.all()
    serializer_class = serializers.CardSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        account = Account.objects.all().filter(user=self.request.user).order_by("created_at").first()
        
        serializer = serializers.CardSerializer(data=request.data)
        
        serializer.initial_data["account"] = account.pk
        
        if serializer.is_valid():
            if account.balance >= 100:
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({'approved': False, 'message': 'Seu saldo deve ser maior que 100'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        """Pegar contas para usuários autenticados"""
        queryset = self.queryset
        return queryset.filter(account=(Account.objects.all().filter(user=self.request.user).order_by("created_at").first())).order_by("created_at").distinct()
        
    
    
class LoanViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Loan.objects.all()
    serializer_class = serializers.LoanSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Pegar empréstimos para usuários autenticados"""
        queryset = self.queryset
        return queryset.filter(account=(Account.objects.all().filter(user=self.request.user).order_by("created_at").first())).order_by("created_at").distinct()
    
    def create(self, request, *args, **kwargs):
        account = Account.objects.all().filter(user=self.request.user).order_by("created_at").first()
        
        serializer = serializers.LoanSerializer(data=request.data)
        
        serializer.initial_data["account"] = account.pk
        
        if serializer.is_valid():
            if account.balance >= 100:
                
                account.balance += serializer.validated_data.get('value')
                account.save()
                
                loan = Loan(
                    value=serializer.validated_data.get('value'),
                    payments=serializer.validated_data.get('payments'),
                    approved=True,
                    payed=False,
                    account=serializer.validated_data.get('account')
                )
                loan.save()
                return Response({'approved': True}, status=status.HTTP_201_CREATED)
            else:
                loan = Loan(
                    value=serializer.validated_data.get('value'),
                    payments=serializer.validated_data.get('payments'),
                    approved=False,
                    payed=False,
                    account=serializer.validated_data.get('account')
                )
                loan.save()
                return Response({'approved': False, 'message': 'Seu saldo deve ser maior que 100'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)