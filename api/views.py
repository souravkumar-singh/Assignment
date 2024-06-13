from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Loan, Payment, Billing, DuePayment
from .serializers import RegisterUserSerializer, ApplyLoanSerializer, MakePaymentSerializer, LoanDetailSerializer, BillingSerializer, DuePaymentSerializer,UserProfileSerializer
from .tasks import calculate_credit_score
import datetime
from decimal import Decimal

@api_view(['GET'])
def new_view(request):
    dic = {
        'to_register': 'api/register-user/',
        'to_apply_loan': 'api/apply-loan/',
        'to_make_payment': 'api/make-payment/',
        'to_get_statement': 'api/get-statement/',
    }
    return Response(dic)

@api_view(['POST'])
def register_user(request):
    serializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
        user_profile = serializer.save()
        csv_file_path = '/Users/sourav/Desktop/Bright-money-assignment/api/Data.csv' 
        calculate_credit_score.delay(csv_file_path=csv_file_path, aadhar_id=user_profile.aadhar_id)
        return Response({"unique_user_id": user_profile.id}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def apply_loan(request):
    user_profile_id = request.data.get('user')
    if not user_profile_id:
        return Response({'error': 'User ID is required'}, status=400)
    
    user_profile = get_object_or_404(UserProfile, id=user_profile_id)
    if user_profile.credit_score is None:
        return Response({'error': 'Credit score is not available'}, status=400)
    
    if user_profile.credit_score < 450:
        return Response({'error': 'Credit score is too low'}, status=400)
    if user_profile.annual_income < 150000:
        return Response({'error': 'Annual income is too low'}, status=400)
    if request.data.get('loan_amount') > 5000:
        return Response({'error': 'Loan amount exceeds limit'}, status=400)

    serializer = ApplyLoanSerializer(data=request.data)
    if serializer.is_valid():
        loan = serializer.save()
        return Response({"Loan_id": loan.id}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def make_payment(request):
    try:
        # Extract data from request payload
        loan_id = request.data.get('Loan_id')
        payment_amount = Decimal(request.data.get('amount', '0.00'))  # Ensure to convert amount to Decimal
        
        # Validate loan_id and payment_amount
        if not loan_id or payment_amount <= 0:
            return Response({'error': 'Invalid loan ID or payment amount.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the loan object
        loan = get_object_or_404(Loan, id=loan_id)

        # Check if payment amount is valid
        if payment_amount > loan.emi_amount:
            return Response({'error': 'Payment amount exceeds the EMI amount.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if loan is overdue
        if loan.next_due_date < date.today():
            return Response({'error': 'Loan is overdue. Cannot make payment.'}, status=status.HTTP_400_BAD_REQUEST)

        # Process payment
        if payment_amount >= loan.emi_amount:
            # Full EMI payment
            loan.total_amount_paid += payment_amount
            loan.remaining_emis -= 1
            loan.emi_due_dates.pop(0)
            loan.emi_due_amounts.pop(0)
        else:
            # Partial payment
            loan.total_amount_paid += payment_amount
            if loan.emi_due_amounts[0] is not None:
                loan.emi_due_amounts[0] -= payment_amount

        # Update loan details
        loan.last_payment_date = date.today()
        if loan.remaining_emis > 0:
            loan.next_due_date = loan.emi_due_dates[0]

        # Save loan object
        loan.save()

        # Serialize loan object and return response
        serializer = LoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
@api_view(['GET'])
def get_statement(request):
    loan_id = request.query_params.get('loan_id')
    loan = get_object_or_404(Loan, id=loan_id)
    
    if loan.closed:
        return Response({'error': 'Loan is closed'}, status=400)

    payments = Payment.objects.filter(loan=loan).order_by('date')
    upcoming_emis = DuePayment.objects.filter(billing__user=loan.user, amount_due__gt=0).order_by('billing__billing_date')

    past_transactions = []
    for payment in payments:
        past_transactions.append({
            'Date': payment.date,
            'Principal': loan.principal_balance,
            'Interest': loan.interest_rate,
            'Amount_paid': payment.amount
        })

    upcoming_transactions = []
    for emi in upcoming_emis:
        upcoming_transactions.append({
            'Date': emi.billing.billing_date,
            'Amount_due': emi.amount_due
        })

    return Response({
        'past_transactions': past_transactions,
        'upcoming_transactions': upcoming_transactions
    })