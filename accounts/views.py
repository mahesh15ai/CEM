from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from accounts.models import User
from students.models import StudentProfile

def login_view(request):
    # जर आधीच लॉगिन असेल तर रोलनुसार योग्य पानावर पाठवा
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff or getattr(request.user, 'is_admin', False):
            return redirect('student_list')
        return redirect('event_list')

    if request.method == 'POST':
        input_identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        target_username = input_identifier
        
        # 1. Student ID जुळतोय का ते तपासा
        student_profile = StudentProfile.objects.filter(student_id__iexact=input_identifier).select_related('user').first()
        if student_profile and student_profile.user:
            target_username = student_profile.user.username
        else:
            # 2. Email ID जुळतोय का ते तपासा
            user_by_email = User.objects.filter(email__iexact=input_identifier).first()
            if user_by_email:
                target_username = user_by_email.username

        # Authenticate User
        user = authenticate(request, username=target_username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                
                # Role-Based Clean Redirect
                if user.is_superuser or user.is_staff or getattr(user, 'is_admin', False):
                    return redirect('student_list')
                else:
                    return redirect('event_list')
            else:
                messages.error(request, "This account has been disabled.")
        else:
            messages.error(request, "Invalid username/Student ID or password.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


def qr_login_view(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data', '').strip()
        
        # Clean QR prefix: "STUDENT:VBM20260001", "STUDENT_PASS:VBM20260001", or raw "VBM20260001"
        student_id = qr_data.replace('STUDENT_PASS:', '').replace('STUDENT:', '').strip()

        student = StudentProfile.objects.filter(student_id__iexact=student_id).select_related('user').first()

        if student and student.user:
            user = student.user
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}! Logged in via Identity QR.")
            
            # Redirect Student to Events List
            return redirect('event_list')
        else:
            messages.error(request, "Invalid QR Pass or Student record not found.")
            return redirect('login')

    return render(request, 'accounts/qr_login.html')