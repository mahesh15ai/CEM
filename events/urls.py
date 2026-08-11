from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('register/<int:event_id>/', views.register_event, name='register_event'),
    path('pass/<int:event_id>/', views.event_pass, name='event_pass'),
    
    # Scanner & Entry Attendance URLs
    path('scan/<int:event_id>/', views.scan_event_pass, name='scan_event_pass'),
    path('process-qr/', views.process_event_qr, name='process_event_qr'),
    path('records/<int:event_id>/', views.event_attendance_records, name='event_attendance_records'),
    
]