from django.core.management.base import BaseCommand
import pandas as pd
from voters.models import Voter
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import voters from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to Excel file')

    def handle(self, *args, **options):
        try:
            file_path = options['excel_file']
            self.stdout.write(f'Reading Excel file: {file_path}')

            # Read Excel file
            df = pd.read_excel(file_path)
            self.stdout.write(f'Found {len(df)} records')

            # Convert DataFrame to list of dictionaries
            voters_data = []
            for index, row in df.iterrows():
                data = {}
                for column in df.columns:
                    value = row[column]
                    # Handle different data types
                    if pd.isna(value):
                        data[str(column)] = ''
                    elif isinstance(value, pd.Timestamp):
                        data[str(column)] = value.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        data[str(column)] = str(value).strip()

                voters_data.append(Voter(data=data))

                if index > 0 and index % 1000 == 0:
                    self.stdout.write(f'Processed {index} records')

            # Clear existing data if needed
            # Voter.objects.all().delete()

            # Bulk create voters
            self.stdout.write('Importing voters to database...')
            with transaction.atomic():
                Voter.objects.bulk_create(voters_data, batch_size=1000)

            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {len(voters_data)} voters')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing voters: {str(e)}')
            )
            logger.error(f'Error importing voters: {str(e)}', exc_info=True)