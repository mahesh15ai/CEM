from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from students.models import StudentProfile
from .models import AttendanceRecord

@login_required
def scan_attendance(request):
    is_admin_user = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'is_admin', False)
    if not is_admin_user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Access denied.'}, status=403)
        messages.error(request, "Access denied. Admin permissions required.")
        return redirect('dashboard')

    if request.method == 'POST':
        qr_data = request.POST.get('qr_data', '').strip()
        student_id = qr_data.replace('STUDENT:', '').strip()

        student = StudentProfile.objects.filter(student_id=student_id).first()

        if student:
            today = timezone.now().date()
            record, created = AttendanceRecord.objects.get_or_create(
                student=student,
                date=today,
                defaults={
                    'status': 'Present',
                    'marked_by': request.user.username
                }
            )

            # Check if AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                if created:
                    return JsonResponse({
                        'status': 'success',
                        'message': f"Marked PRESENT for {student.user.get_full_name()}",
                        'student_name': student.user.get_full_name(),
                        'student_id': student.student_id,
                        'roll_number': student.roll_number,
                        'time': timezone.now().strftime("%I:%M %p"),
                        'is_new': True
                    })
                else:
                    return JsonResponse({
                        'status': 'warning',
                        'message': f"Already marked today for {student.user.get_full_name()}",
                        'is_new': False
                    })
            else:
                if created:
                    messages.success(request, f"✅ Attendance Marked PRESENT for {student.user.get_full_name()}")
                else:
                    messages.warning(request, f"⚠️ Attendance ALREADY MARKED today for {student.user.get_full_name()}")
                return redirect('scan_attendance')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Invalid Student QR Code!'}, status=400)
            messages.error(request, "❌ Invalid QR Pass!")
            return redirect('scan_attendance')

    today_records = AttendanceRecord.objects.select_related('student__user').filter(
        date=timezone.now().date()
    ).order_by('-time')[:20]

    return render(request, 'attendance/scan.html', {'recent_records': today_records})