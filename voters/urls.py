from django.urls import path
from . import views
from .admin import VoterAdmin

app_name = 'voters'

urlpatterns = [
    path('list/', views.voter_list, name='voter-list'),
    path('/api/filter-voters/', views.filter_voters, name='filter-voters'),
    path('admin/voters/voter/api/bulk-delete/', VoterAdmin.bulk_delete_voters, name= 'bulk-delete-voters'),
    path('admin/voters/send-notification/', views.send_notification, name='send-notification'),
    # path('/admin/voters/voter/api/filter-voters/', views.get_filter_options, name='get-filter-options'),
    path('api/filter-voters/', views.filter_voters, name='filter-voters'),
    path('process-excel/', views.process_excel, name='process-excel'),
    path('get-filtered-data/', views.get_filtered_data, name='get-filtered-data'),
]