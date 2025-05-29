from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Q
import pandas as pd
import json
import logging
from datetime import datetime

from . import views
from .models import VoterField, Voter
from .forms import VoterForm
from notifications.models import NotificationType, NotificationTemplate, NotificationLog
from notifications.utils import NotificationSender

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('voter_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define Excel fields and mappings
EXCEL_FIELDS = [
    'MLC CONSTITUNCY', 'ASSEMBLY', 'MANDAL', 'TOWN', 'VILLAGE', 'PSNO',
    'LOCATION', 'PS ADDRESS', 'STREET', 'HNO', 'SNO', 'CARD NO',
    'VOTER NAME', 'MOBILE NO', 'AGE', 'GENDER', 'REL NAME', 'RELATION',
    'VOTER STATUS', 'PARTY', 'CASTE', 'CATEGORY', 'VERIFY STATUS'
]

EXCEL_FIELD_MAPPING = {
    'MLC CONSTITUNCY': 'mlc_constituncy',
    'ASSEMBLY': 'assembly',
    'MANDAL': 'mandal',
    'TOWN': 'town',
    'VILLAGE': 'village',
    'PSNO': 'psno',
    'LOCATION': 'location',
    'PS ADDRESS': 'ps_address',
    'STREET': 'street',
    'HNO': 'hno',
    'SNO': 'sno',
    'CARD NO': 'card_no',
    'VOTER NAME': 'voter_name',
    'MOBILE NO': 'mobile_no',
    'AGE': 'age',
    'GENDER': 'gender',
    'REL NAME': 'rel_name',
    'RELATION': 'relation',
    'VOTER STATUS': 'voter_status',
    'PARTY': 'party',
    'CASTE': 'caste',
    'CATEGORY': 'category',
    'VERIFY STATUS': 'verify_status'
}

REQUIRED_FIELDS = ['MLC CONSTITUNCY', 'ASSEMBLY', 'MANDAL', 'SNO', 'MOBILE NO']

@admin.register(VoterField)
class VoterFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_type', 'is_required', 'created_at', 'updated_at')
    list_filter = ('field_type', 'is_required')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    form = VoterForm
    change_list_template = 'admin/voters/voter/change_list.html'
    list_per_page = 50

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.upload_excel_view, name='voter-upload-excel'),
            path('process-excel/', self.process_excel, name='process-excel'),
            path('api/get-filtered-data/', self.get_filtered_data, name='get-filtered-data'),
            path('api/add-voter/', self.add_voter, name='add-voter'),
            path('api/voter/<int:pk>/delete/', self.delete_voter, name='voter-delete'),
            path('api/bulk-delete-voters/', self.bulk_delete_voters, name='bulk-delete-voters'),
            path('api/voter/<int:pk>/edit/', self.edit_voter, name='voter-edit'),
            path('send-notification/', self.send_notification, name='send-notification'),
            path('api/filter-voters/', self.filter_voters_view, name='filter-voters'),

        ]
        return custom_urls + urls

    def filter_voters_view(self, request):
        try:
            # Get filter parameters
            mlc_constituncy = request.GET.get('mlc_constituncy')
            assembly = request.GET.get('assembly')
            mandal = request.GET.get('mandal')
            village = request.GET.get('village')

            # Start with all voters
            queryset = self.get_queryset(request)

            # Apply filters
            if mlc_constituncy:
                queryset = queryset.filter(data__contains={'MLC CONSTITUNCY': mlc_constituncy})
            if assembly:
                queryset = queryset.filter(data__contains={'ASSEMBLY': assembly})
            if mandal:
                queryset = queryset.filter(data__contains={'MANDAL': mandal})
            if village:
                queryset = queryset.filter(data__contains={'VILLAGE': village})

            # Format data for response
            voters_data = []
            for voter in queryset:
                voter_dict = {
                    'id': voter.id,
                    'mlc_constituncy': voter.data.get('MLC CONSTITUNCY', ''),
                    'assembly': voter.data.get('ASSEMBLY', ''),
                    'mandal': voter.data.get('MANDAL', ''),
                    'village': voter.data.get('VILLAGE', ''),
                    'mobile_no': voter.data.get('MOBILE NO', ''),
                    'sno': voter.data.get('SNO', ''),
                    # Add any other fields you need
                }
                voters_data.append(voter_dict)

            # Print debug information
            print(f"Found {len(voters_data)} voters matching the filters")
            if voters_data:
                print(f"Sample voter data: {voters_data[0]}")

            return JsonResponse({
                'success': True,
                'total_count': len(voters_data),
                'data': voters_data
            })

        except Exception as e:
            print(f"Error in filter_voters_view: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #
    #     # Get filter values from request
    #     mlc_filter = request.GET.get('mlc_constituncy')
    #     assembly_filter = request.GET.get('assembly')
    #     mandal_filter = request.GET.get('mandal')
    #     village_filter = request.GET.get('village')
    #
    #     # Apply filters using case-insensitive contains
    #     if mlc_filter:
    #         queryset = queryset.filter(data__MLC_CONSTITUNCY__icontains=mlc_filter)
    #     if assembly_filter:
    #         queryset = queryset.filter(data__ASSEMBLY__icontains=assembly_filter)
    #     if mandal_filter:
    #         queryset = queryset.filter(data__MANDAL__icontains=mandal_filter)
    #     if village_filter:
    #         queryset = queryset.filter(data__VILLAGE__icontains=village_filter)
    #
    #     return queryset
    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # Get filter values from request
        mlc_filter = request.GET.get('mlc_constituncy')
        assembly_filter = request.GET.get('assembly')
        mandal_filter = request.GET.get('mandal')
        village_filter = request.GET.get('village')

        # Apply filters using case-insensitive contains
        if mlc_filter:
            queryset = queryset.filter(data__MLC_CONSTITUNCY__icontains=mlc_filter)
        if assembly_filter:
            queryset = queryset.filter(data__ASSEMBLY__icontains=assembly_filter)
        if mandal_filter:
            queryset = queryset.filter(data__MANDAL__icontains=mandal_filter)
        if village_filter:
            queryset = queryset.filter(data__VILLAGE__icontains=village_filter)

        return queryset

    def get_filtered_data(self, request):
        """
        API endpoint to get filtered dropdown data
        """
        try:
            filter_type = request.GET.get('type')
            parent_value = request.GET.get('value')

            if not filter_type:
                return JsonResponse({'error': 'Filter type is required'}, status=400)

            queryset = self.get_queryset(request)

            if filter_type == 'mlc':
                values = queryset.values_list('data__MLC CONSTITUNCY', flat=True)
            elif filter_type == 'assembly' and parent_value:
                values = queryset.filter(
                    data__contains={'MLC CONSTITUNCY': parent_value}
                ).values_list('data__ASSEMBLY', flat=True)
            elif filter_type == 'mandal' and parent_value:
                values = queryset.filter(
                    data__contains={'ASSEMBLY': parent_value}
                ).values_list('data__MANDAL', flat=True)
            elif filter_type == 'village' and parent_value:
                values = queryset.filter(
                    data__contains={'MANDAL': parent_value}
                ).values_list('data__VILLAGE', flat=True)
            else:
                return JsonResponse({'error': 'Invalid filter type or missing parent value'}, status=400)

            # Remove duplicates, None values, and empty strings, then sort
            unique_values = sorted(set(filter(None, values)))
            return JsonResponse(unique_values, safe=False)

        except Exception as e:
            logger.error(f"Error in get_filtered_data: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


    def get_assemblies(self, request):
        mlc = request.GET.get('mlc', '')
        try:
            # Use raw SQL to get unique assemblies
            assemblies = Voter.objects.filter(
                data__contains={'MLC CONSTITUNCY': mlc}
            ).values_list('data__ASSEMBLY', flat=True)
            # Remove duplicates and None values
            unique_assemblies = sorted(set(filter(None, assemblies)))
            return JsonResponse(list(unique_assemblies), safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def get_mandals(self, request):
        assembly = request.GET.get('assembly', '')
        try:
            # Use raw SQL to get unique mandals
            mandals = Voter.objects.filter(
                data__contains={'ASSEMBLY': assembly}
            ).values_list('data__MANDAL', flat=True)
            # Remove duplicates and None values
            unique_mandals = sorted(set(filter(None, mandals)))
            return JsonResponse(list(unique_mandals), safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def get_villages(self, request):
        mandal = request.GET.get('mandal', '')
        try:
            # Use raw SQL to get unique villages
            villages = Voter.objects.filter(
                data__contains={'MANDAL': mandal}
            ).values_list('data__VILLAGE', flat=True)
            # Remove duplicates and None values
            unique_villages = sorted(set(filter(None, villages)))
            return JsonResponse(list(unique_villages), safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def get_list_display(self, request):
        # Define custom display methods for each field
        def get_field_display(field_name):
            def field_display(obj):
                return obj.data.get(field_name, '') if obj.data else ''

            field_display.short_description = field_name
            return field_display

        # Create a list of display functions for each Excel field
        display_fields = []
        for field_name in EXCEL_FIELD_MAPPING.keys():
            func = get_field_display(field_name)
            setattr(self, f'get_{field_name.lower().replace(" ", "_")}', func)
            display_fields.append(f'get_{field_name.lower().replace(" ", "_")}')

        return display_fields


    def upload_excel_view(self, request):
        return render(request, 'admin/voters/voter/upload_excel.html', {
            'title': 'Upload Excel File',
            'current_datetime': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_user': request.user.username,
        })

    @method_decorator(csrf_protect)
    @method_decorator(staff_member_required)
    def process_excel(self, request):
        if request.method == 'POST' and request.FILES.get('excel_file'):
            try:
                excel_file = request.FILES['excel_file']

                # Read the Excel file
                df = pd.read_excel(excel_file)

                # Validate required columns
                missing_columns = [field for field in REQUIRED_FIELDS if field not in df.columns]
                if missing_columns:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Required columns missing: {", ".join(missing_columns)}'
                    }, status=400)

                # Process each row
                success_count = 0
                error_count = 0
                errors = []

                for index, row in df.iterrows():
                    try:
                        # Convert row to dictionary
                        voter_data = row.to_dict()

                        # Clean up NaN values
                        voter_data = {k: ('' if pd.isna(v) else str(v)) for k, v in voter_data.items()}

                        # Create voter instance
                        voter = Voter.objects.create(
                            mlc_constituncy=voter_data.get('MLC CONSTITUNCY', ''),
                            assembly=voter_data.get('ASSEMBLY', ''),
                            mandal=voter_data.get('MANDAL', ''),
                            sno=voter_data.get('SNO', ''),
                            mobile_no=voter_data.get('MOBILE NO', ''),
                            data=voter_data
                        )
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        errors.append(f'Row {index + 2}: {str(e)}')

                return JsonResponse({
                    'status': 'success',
                    'data': {
                        'total_processed': len(df),
                        'success_count': success_count,
                        'error_count': error_count,
                        'errors': errors
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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Get filtered queryset
        queryset = self.get_queryset(request)

        # Get unique values for MLC Constituencies
        mlc_values = sorted(set(
            voter.data.get('MLC CONSTITUNCY', '')
            for voter in queryset
            if voter.data and voter.data.get('MLC CONSTITUNCY')
        ))

        # Current filter values
        current_filters = {
            'mlc_constituncy': request.GET.get('mlc_constituncy', ''),
            'assembly': request.GET.get('assembly', ''),
            'mandal': request.GET.get('mandal', ''),
            'village': request.GET.get('village', ''),
        }

        extra_context.update({
            'current_datetime': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_user': request.user.username,
            'excel_fields': EXCEL_FIELDS,
            'unique_mlc': mlc_values,
            'current_filters': current_filters,
            'notification_types': NotificationType.objects.all(),
            'notification_templates': NotificationTemplate.objects.select_related('notification_type').all(),
            'templates_by_type': self.get_templates_by_type(),
            'notification_channels': [
                {'id': 'SMS', 'name': 'SMS'},
                {'id': 'WA', 'name': 'WhatsApp'},
                {'id': 'BOTH', 'name': 'Both (SMS & WhatsApp)'}
            ]
        })

        return super().changelist_view(request, extra_context)

    def get_templates_by_type(self):
        templates = NotificationTemplate.objects.select_related('notification_type').all()
        templates_by_type = {}
        for template in templates:
            if template.notification_type_id not in templates_by_type:
                templates_by_type[template.notification_type_id] = []
            templates_by_type[template.notification_type_id].append({
                'id': template.id,
                'name': template.name
            })
        return templates_by_type


    @method_decorator(csrf_protect)
    @method_decorator(staff_member_required)
    def send_notification(self, request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                type_id = data.get('type_id')
                template_id = data.get('template_id')
                channel = data.get('channel')
                voter_ids = data.get('voter_ids', [])

                if not all([type_id, template_id, channel, voter_ids]):
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing required parameters'
                    }, status=400)

                # Get voters and template
                voters = Voter.objects.filter(id__in=voter_ids)
                template = NotificationTemplate.objects.get(id=template_id)

                # Initialize notification sender
                sender = NotificationSender()
                results = {
                    'success_count': 0,
                    'failure_count': 0,
                    'errors': []
                }

                for voter in voters:
                    try:
                        if not voter.mobile_no:
                            raise ValueError(f"Voter {voter.id} has no mobile number")

                        notification_log = NotificationLog.objects.create(
                            recipient=voter.mobile_no,
                            template=template,
                            channel=channel,
                            status=NotificationLog.Status.PENDING
                        )

                        success, error = sender.send_notification(notification_log)

                        if success:
                            results['success_count'] += 1
                        else:
                            results['failure_count'] += 1
                            results['errors'].append({
                                'voter_id': voter.id,
                                'mobile': voter.mobile_no,
                                'error': error
                            })
                    except Exception as e:
                        logger.error(f"Error processing voter {voter.id}: {str(e)}")
                        results['failure_count'] += 1
                        results['errors'].append({
                            'voter_id': voter.id,
                            'mobile': getattr(voter, 'mobile_no', 'N/A'),
                            'error': str(e)
                        })

                return JsonResponse({
                    'success': True,
                    'data': {
                        'total_sent': results['success_count'],
                        'total_failed': results['failure_count'],
                        'errors': results['errors'] if results['errors'] else None
                    }
                })

            except Exception as e:
                logger.error(f"Error in send_notification view: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)

        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        }, status=405)

    @method_decorator(csrf_protect)
    @method_decorator(staff_member_required)
    def add_voter(self, request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)

                # Validate required fields
                missing_fields = [field for field in REQUIRED_FIELDS if not data.get(field)]
                if missing_fields:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Required fields missing: {", ".join(missing_fields)}'
                    }, status=400)

                # Create voter instance
                voter = Voter.objects.create(
                    mlc_constituncy=data.get('MLC CONSTITUNCY', ''),
                    assembly=data.get('ASSEMBLY', ''),
                    mandal=data.get('MANDAL', ''),
                    sno=data.get('SNO', ''),
                    mobile_no=data.get('MOBILE NO', ''),
                    data=data
                )

                return JsonResponse({
                    'status': 'success',
                    'message': 'Voter added successfully',
                    'voter': {
                        'id': voter.id,
                        'mlc_constituncy': voter.mlc_constituncy,
                        'assembly': voter.assembly,
                        'mandal': voter.mandal,
                        'sno': voter.sno,
                        'mobile_no': voter.mobile_no
                    }
                })

            except Exception as e:
                logger.error(f"Error adding voter: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)

        return JsonResponse({
            'status': 'error',
            'message': 'Invalid method'
        }, status=405)

    @method_decorator(csrf_protect)
    @method_decorator(staff_member_required)
    def delete_voter(self, request, pk):
        if request.method == 'POST':
            try:
                voter = Voter.objects.get(pk=pk)
                voter.delete()
                return JsonResponse({'success': True})
            except Voter.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Voter not found'
                }, status=404)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        return JsonResponse({
            'success': False,
            'error': 'Invalid method'
        }, status=405)

    @method_decorator(csrf_protect)
    @method_decorator(staff_member_required)
    def bulk_delete_voters(self, request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                voter_ids = data.get('voter_ids', [])

                if not voter_ids:
                    return JsonResponse({
                        'success': False,
                        'error': 'No voters selected'
                    }, status=400)

                Voter.objects.filter(id__in=voter_ids).delete()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        return JsonResponse({
            'success': False,
            'error': 'Invalid method'
        }, status=405)

    @method_decorator(csrf_protect)
    @method_decorator(staff_member_required)
    def edit_voter(self, request, pk):
        if request.method == 'POST':
            try:
                voter = Voter.objects.get(pk=pk)
                data = json.loads(request.body)

                # Update voter fields
                for excel_name, model_field in EXCEL_FIELD_MAPPING.items():
                    if excel_name in data:
                        setattr(voter, model_field, data[excel_name])
                        voter.data[excel_name] = data[excel_name]

                voter.save()
                return JsonResponse({'success': True})
            except Voter.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Voter not found'
                }, status=404)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        return JsonResponse({
            'success': False,
            'error': 'Invalid method'
        }, status=405)