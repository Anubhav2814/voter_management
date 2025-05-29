from django.core.management.base import BaseCommand
import pandas as pd
from voters.models import Voter
from django.db import transaction


class Command(BaseCommand):
    help = 'Import voters from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to Excel file')

    def handle(self, *args, **options):
        try:
            excel_file = options['excel_file']
            df = pd.read_excel(excel_file)

            # Convert all column names to uppercase
            df.columns = [col.upper() for col in df.columns]

            # Create voters in batch
            voters_to_create = []
            for _, row in df.iterrows():
                # Convert row to dictionary and handle NaN values
                voter_data = {}
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value):
                        voter_data[col] = ''
                    elif isinstance(value, (int, float)):
                        voter_data[col] = str(int(value))
                    else:
                        voter_data[col] = str(value).strip()

                voters_to_create.append(Voter(data=voter_data))

            # Use bulk_create for better performance
            with transaction.atomic():
                Voter.objects.bulk_create(voters_to_create, batch_size=1000)

            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {len(voters_to_create)} voters')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing voters: {str(e)}')
            )