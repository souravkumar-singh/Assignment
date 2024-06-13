from .models import Billing, DuePayment, Loan
from datetime import date, timedelta
from django.utils import timezone
from decimal import Decimal

def run_billing():
    today = timezone.now().date()
    loans = Loan.objects.filter(closed=False)
    
    for loan in loans:
        billing_date = loan.disbursement_date + timedelta(days=30)
        if today >= billing_date:
            due_date = billing_date + timedelta(days=15)
            apr = loan.interest_rate / Decimal('365')
            interest_accrued = apr * loan.principal_balance * Decimal(30)
            min_due = (loan.principal_balance * Decimal('0.03')) + interest_accrued

            billing = Billing.objects.create(
                user=loan.user,
                billing_date=billing_date,
                due_date=due_date
            )

            DuePayment.objects.create(
                billing=billing,
                amount_due=loan.principal_balance + interest_accrued,
                min_due=min_due,
                principal_due=loan.principal_balance,
                interest_due=interest_accrued
            )
