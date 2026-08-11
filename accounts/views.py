from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name if user.first_name else user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid credentials provided.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from accounts.models import User
from students.models import StudentProfile

def qr_login_view(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data', '').strip()
        
        # QR text format cleans: "STUDENT:VBM20260001" or "VBM20260001"
        student_id = qr_data.replace('STUDENT:', '').strip()

        student = StudentProfile.objects.filter(student_id=student_id).select_related('user').first()

        if student and student.user:
            user = student.user
            # Log the student in automatically
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}! Logged in via Identity QR.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid QR Pass or Student record not found.")
            return redirect('login')

    return render(request, 'accounts/qr_login.html')