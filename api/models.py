from django.db import models
from django.contrib.auth.models import User
import uuid
from decimal import Decimal
from django.utils import timezone

class SavingsTransaction(models.Model):
    aadhar_id = models.CharField(max_length=40)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10)

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    aadhar_id = models.CharField(max_length=40, unique=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    credit_score = models.IntegerField(null=True, blank=True)
    email = models.EmailField(max_length=40)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now) 

class Loan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=20, default='Credit Card')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2)
    term_period = models.IntegerField()
    disbursement_date = models.DateField()
    emi_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    closed = models.BooleanField(default=False)
    principal_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

class Billing(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    billing_date = models.DateField()
    due_date = models.DateField()

class DuePayment(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    min_due = models.DecimalField(max_digits=12, decimal_places=2)
    principal_due = models.DecimalField(max_digits=12, decimal_places=2)
    interest_due = models.DecimalField(max_digits=12, decimal_places=2)