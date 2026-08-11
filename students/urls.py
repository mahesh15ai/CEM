from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.student_list, name='student_list'),
    path('add/', views.add_student, name='add_student'),
    path('bulk-add/', views.bulk_add_students, name='bulk_add_students'),
    path('pass/<int:student_id>/', views.student_pass, name='student_pass'),
]