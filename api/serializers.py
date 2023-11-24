from rest_framework import serializers
from core.models import Account, Address, Card, Transaction, Loan, LoanPayment
from user.serializers import UserSerializer

class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    
    class Meta:
        model = Account
        fields = ['id', 'agency', 'number', 'user']
        read_only_fields = ['id', 'agency', 'number', 'user']
        
class AccountDetailSerializer(AccountSerializer):
    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ['id', 'balance', 'created_at']
        read_only_fields = AccountSerializer.Meta.read_only_fields + ['id', 'balance', 'created_at']
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    sender = AccountSerializer(many=False, read_only=True)
    recipient = AccountSerializer(many=False, read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'value', 'description', 'sender', 'card', 'recipient', 'created_at']

class TransactionDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['value', 'description', 'recipient']
        
class TransactionWithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['value', 'description', 'sender']

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class LoanPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanPayment
        fields = '__all__'

class DepositSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        model = Transaction
        fields = ['value']

class WithdrawSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        model = Transaction
        fields = ['value']