from django.urls import path
from . import views

urlpatterns = [
    # Dashboard Route
    path('dashboard/', views.student_dashboard, name='student_dashboard'),

    # Admin Management Routes
    path('list/', views.student_list, name='student_list'),
    path('add/', views.add_student, name='add_student'),
    path('edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('bulk-add/', views.bulk_add_students, name='bulk_add_students'),
    path('pass/<int:student_id>/', views.student_pass, name='student_pass'),
    path('export/', views.export_students_excel, name='export_students_excel'), # <--- ही लिंक आवश्यक आहे

    # Banner & Announcement Routes
    path('add-banner/', views.add_banner, name='add_banner'),
    path('add-announcement/', views.add_announcement, name='add_announcement'),

    # Student Self-Service Routes
    path('my-profile/', views.student_profile_view, name='student_profile_view'),
    path('edit-my-profile/', views.edit_my_profile, name='edit_my_profile'),
]