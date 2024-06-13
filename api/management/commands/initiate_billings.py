import csv
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from api.models import SavingsTransaction, UserProfile
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate the database with data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header

            for row_idx, row in enumerate(reader, start=1):
                try:
                    aadhar_id = row[0]
                    transaction_date = row[1]
                    amount = Decimal(row[3])
                    transaction_type = row[2]

                    # Create SavingsTransaction records
                    SavingsTransaction.objects.create(
                        aadhar_id=aadhar_id,
                        transaction_date=transaction_date,
                        amount=amount,
                        transaction_type=transaction_type
                    )

                    # Create dummy UserProfile with unique UUID and initial values if not exists
                    if not UserProfile.objects.filter(aadhar_id=aadhar_id).exists():
                        user = User.objects.create_user(
                            username=f"user_{aadhar_id}", 
                            password="password"
                        )
                        UserProfile.objects.create(
                            id=uuid.uuid4(),
                            user=user,
                            aadhar_id=aadhar_id,
                            annual_income=Decimal('0.00'),
                            email=f"user_{aadhar_id}@example.com",
                            created_at=timezone.now(),
                            updated_at=timezone.now()
                        )
                except (IndexError, InvalidOperation) as e:
                    self.stdout.write(self.style.WARNING(f'Skipped row {row_idx} due to error: {row}'))
                    continue  # Skip to the next row

        self.stdout.write(self.style.SUCCESS('Database populated successfully'))
