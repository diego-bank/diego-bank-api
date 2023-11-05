from rest_framework import serializers
from core.models import Account, Address, Card, Transaction, Loan, LoanPayment

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id','agency', 'number']
        read_only_fields = ['id','agency', 'number']
        
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
    class Meta:
        model = Transaction
        fields = ['value', 'description', 'sender', 'card', 'recipient']

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
        fields = ['value']

class WithdrawSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        fields = ['value']