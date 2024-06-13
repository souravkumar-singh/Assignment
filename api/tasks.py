from LoanManagement.celery import app
from api.models import UserProfile
import pandas as pd
from django.db import transaction

@app.task
def calculate_credit_score(csv_file_path, aadhar_id):
    account_balance = 0
    found_aadhar = False

    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file_path)

        # Filter transactions for the given Aadhar ID
        transactions = df[df['user'] == aadhar_id]

        if not transactions.empty:
            found_aadhar = True
            for index, row in transactions.iterrows():
                if row['transaction_type'].strip().upper() == 'CREDIT':
                    account_balance += float(row['amount'])
                elif row['transaction_type'].strip().upper() == 'DEBIT':
                    account_balance -= float(row['amount'])

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

    # Calculate the credit score based on the account balance
    if found_aadhar:
        if account_balance >= 1000000:
            credit_score = 900
        elif account_balance <= 100000:
            credit_score = 300
        else:
            credit_score = 600 + (int((account_balance - 100000) / 15000) * 10)
    else:
        # Set the default credit score to 600 if no Aadhar ID was found
        credit_score = 600

    # Update the user profile if the Aadhar ID was found
    if found_aadhar:
        with transaction.atomic():
            try:
                user_profile = UserProfile.objects.get(aadhar_id=aadhar_id)
                user_profile.credit_score = credit_score
                user_profile.save()
                return credit_score
            except UserProfile.DoesNotExist:
                return None
    else:
        return None
