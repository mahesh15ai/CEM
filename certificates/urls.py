from django.urls import path
from . import views

urlpatterns = [
    path('', views.certificate_list, name='certificate_list'),
    path('issue/', views.issue_certificate, name='issue_certificate'),
    path('view/<str:certificate_id>/', views.view_certificate, name='view_certificate'),
]