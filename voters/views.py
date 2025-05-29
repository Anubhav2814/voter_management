from django.shortcuts import render
from django.http import JsonResponse
from .models import Voter, VoterField
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from .models import Voter
from .serializers import VoterSerializer
from notifications.models import NotificationTemplate, NotificationLog
from django.utils import timezone
import requests
from django.conf import settings
import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator
import pandas as pd


# Set up logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_protect)
@method_decorator(staff_member_required)
def process_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            excel_file = request.FILES['excel_file']

            # Read Excel file
            df = pd.read_excel(excel_file)

            # Validate required columns
            required_fields = ['MLC CONSTITUNCY', 'ASSEMBLY', 'MANDAL', 'SNO', 'MOBILE NO']
            missing_columns = [field for field in required_fields if field not in df.columns]

            if missing_columns:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Required columns missing: {", ".join(missing_columns)}'
                }, status=400)

            # Process rows
            success_count = 0
            error_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    # Clean data
                    voter_data = row.to_dict()
                    voter_data = {k: ('' if pd.isna(v) else str(v).strip()) for k, v in voter_data.items()}

                    # Validate required fields
                    invalid_fields = [field for field in required_fields if not voter_data.get(field)]
                    if invalid_fields:
                        raise ValueError(f"Missing required fields: {', '.join(invalid_fields)}")

                    # Create voter
                    voter = Voter.objects.create(
                        mlc_constituncy=voter_data.get('MLC CONSTITUNCY'),
                        assembly=voter_data.get('ASSEMBLY'),
                        mandal=voter_data.get('MANDAL'),
                        sno=voter_data.get('SNO'),
                        mobile_no=voter_data.get('MOBILE NO'),
                        data=voter_data
                    )
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append({
                        'row': index + 2,  # Excel rows start at 1, and we add 1 for header
                        'message': str(e)
                    })

            return JsonResponse({
                'status': 'success',
                'data': {
                    'total_processed': len(df),
                    'success_count': success_count,
                    'error_count': error_count,
                    'errors': errors[:10]  # Limit error messages to first 10
                }
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error processing file: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    }, status=400)


def get_filtered_data(request):
    filter_type = request.GET.get('type')
    parent_value = request.GET.get('value')

    if filter_type == 'assembly':
        data = Voter.objects.filter(mlc_constituncy=parent_value).values_list('assembly', flat=True).distinct()
    elif filter_type == 'mandal':
        data = Voter.objects.filter(assembly=parent_value).values_list('mandal', flat=True).distinct()
    elif filter_type == 'village':
        data = Voter.objects.filter(mandal=parent_value).values_list('village', flat=True).distinct()

    return JsonResponse(list(data), safe=False)

@api_view(['GET'])
def get_filter_options(request):
    try:
        mlc_constituncy = request.GET.get('mlc_constituncy', '')
        assembly = request.GET.get('assembly', '')
        mandal = request.GET.get('mandal', '')

        # Base queryset
        queryset = Voter.objects.all()

        # Apply cascading filters
        if mlc_constituncy:
            queryset = queryset.filter(data__contains={'MLC CONSTITUNCY': mlc_constituncy})
        if assembly:
            queryset = queryset.filter(data__contains={'ASSEMBLY': assembly})
        if mandal:
            queryset = queryset.filter(data__contains={'MANDAL': mandal})

        # Get unique values based on applied filters
        assemblies = list(queryset.values_list('data__ASSEMBLY', flat=True).distinct())
        mandals = list(queryset.values_list('data__MANDAL', flat=True).distinct())
        villages = list(queryset.values_list('data__VILLAGE', flat=True).distinct())  # Changed from LOCATION to VILLAGE

        return Response({
            'success': True,
            'data': {
                'assemblies': assemblies,
                'mandals': mandals,
                'villages': villages,
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        })


from django.core.paginator import Paginator

def filter_voters(request):
    try:
        # Capture filters from GET request
        mlc_constituncy = request.GET.get('mlc_constituncy')
        assembly = request.GET.get('assembly')
        mandal = request.GET.get('mandal')
        village = request.GET.get('village')

        # Filter queryset based on filters
        queryset = Voter.objects.all()
        if mlc_constituncy:
            queryset = queryset.filter(mlc_constituncy=mlc_constituncy)
        if assembly:
            queryset = queryset.filter(assembly=assembly)
        if mandal:
            queryset = queryset.filter(mandal=mandal)
        if village:
            queryset = queryset.filter(village=village)

        # Pagination
        paginator = Paginator(queryset, 10)  # 10 objects per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Prepare response
        data = list(page_obj.object_list.values())
        return JsonResponse({'success': True, 'data': data, 'total_pages': paginator.num_pages})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def voter_list(request):
    voters = Voter.objects.all()
    return JsonResponse({
        'count': voters.count(),
        'fields': list(VoterField.objects.values('name', 'field_type'))
    })


@require_POST
@staff_member_required
def send_notification(request):
    try:
        data = json.loads(request.body)
        template_id = data.get('template_id')
        channel = data.get('channel')
        voter_ids = data.get('voter_ids', [])

        if not all([template_id, channel, voter_ids]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters'
            })

        # Forward the request to notifications app
        response = requests.post(
            f"{request.scheme}://{request.get_host()}/notifications/send/",
            json={
                'template_id': template_id,
                'channel': channel,
                'recipients': voter_ids
            }
        )

        return JsonResponse(response.json())
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})