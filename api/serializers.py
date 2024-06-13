from rest_framework import serializers
from .models import UserProfile, Loan, SavingsTransaction, Payment, Billing, DuePayment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'aadhar_id', 'annual_income', 'email']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        return user_profile


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ('id', 'user', 'loan_type', 'loan_amount', 'interest_rate', 'term_period', 'disbursement_date', 'emi_amount', 'closed', 'principal_balance')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsTransaction
        fields = ('aadhar_id', 'transaction_date', 'amount', 'transaction_type')

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user','aadhar_id', 'annual_income', 'email')

class ApplyLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ('user', 'loan_amount', 'interest_rate', 'term_period', 'disbursement_date')

class MakePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('loan', 'date', 'amount')

class LoanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ('id', 'loan_type', 'loan_amount', 'interest_rate', 'term_period', 'disbursement_date', 'emi_amount', 'closed', 'principal_balance')

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = ('user', 'billing_date', 'due_date')

class DuePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DuePayment
        fields = ('billing', 'amount_due', 'min_due', 'principal_due', 'interest_due')