import qrcode
import io
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from students.models import StudentProfile
from .models import Event, EventRegistration, EventAttendance

@login_required
def event_list(request):
    events = Event.objects.all()
    user_registered_event_ids = []

    if hasattr(request.user, 'student_profile'):
        user_registered_event_ids = EventRegistration.objects.filter(
            student=request.user.student_profile
        ).values_list('event_id', flat=True)

    context = {
        'events': events,
        'registered_event_ids': user_registered_event_ids,
    }
    return render(request, 'events/event_list.html', context)


@login_required
def create_event(request):
    is_admin_user = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'is_admin', False)
    if not is_admin_user:
        messages.error(request, "Access denied. Admin permissions required.")
        return redirect('event_list')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        event_time = request.POST.get('event_time')
        venue = request.POST.get('venue')
        poster = request.FILES.get('poster')

        Event.objects.create(
            title=title,
            description=description,
            event_date=event_date,
            event_time=event_time,
            venue=venue,
            poster=poster
        )
        messages.success(request, f"🎉 Event '{title}' published successfully!")
        return redirect('event_list')

    return render(request, 'events/create_event.html')


@login_required
def register_event(request, event_id):
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "Only students can register for events.")
        return redirect('event_list')

    event = get_object_or_404(Event, id=event_id)
    student = request.user.student_profile

    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        student=student
    )

    if created:
        messages.success(request, f"✅ Successfully registered for {event.title}!")
    else:
        messages.warning(request, f"⚠️ You are already registered for {event.title}.")

    return redirect('event_list')


@login_required
def event_pass(request, event_id):
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "Only students can view event entry passes.")
        return redirect('event_list')

    event = get_object_or_404(Event, id=event_id)
    student = request.user.student_profile
    registration = get_object_or_404(EventRegistration, event=event, student=student)

    # QR format: EVENT_PASS:<event_id>:<student_id>
    qr_content = f"EVENT_PASS:{event.id}:{student.student_id}"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#5C061C", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'event': event,
        'student': student,
        'registration': registration,
        'qr_b64': qr_b64,
    }
    return render(request, 'events/event_pass.html', context)


# --- Event Scanner & Attendance Verification Views ---

@login_required
def scan_event_pass(request, event_id):
    is_admin_user = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'is_admin', False)
    if not is_admin_user:
        messages.error(request, "Access denied. Admin/Staff permission required.")
        return redirect('event_list')

    event = get_object_or_404(Event, id=event_id)
    recent_attendances = EventAttendance.objects.filter(event=event).select_related('student__user').order_by('-entry_time')[:10]

    return render(request, 'events/scan_event_pass.html', {
        'event': event,
        'recent_attendances': recent_attendances
    })


@csrf_exempt
@login_required
def process_event_qr(request):
    if request.method == 'POST':
        qr_code = request.POST.get('qr_code', '').strip()

        # Check QR structure: EVENT_PASS:<event_id>:<student_id>
        if not qr_code.startswith("EVENT_PASS:"):
            return JsonResponse({'status': 'error', 'message': '❌ Invalid Event Pass QR Code!'})

        parts = qr_code.split(':')
        if len(parts) != 3:
            return JsonResponse({'status': 'error', 'message': '❌ Corrupted Pass QR Data!'})

        event_id, student_id = parts[1], parts[2]

        event = Event.objects.filter(id=event_id).first()
        student = StudentProfile.objects.filter(student_id=student_id).first()

        if not event or not student:
            return JsonResponse({'status': 'error', 'message': '❌ Event or Student Profile not found!'})

        # Check registration
        is_registered = EventRegistration.objects.filter(event=event, student=student).exists()
        if not is_registered:
            return JsonResponse({
                'status': 'error', 
                'message': f"⚠️ Student {student.user.get_full_name()} ({student.student_id}) has NOT registered for this event!"
            })

        # Mark attendance record
        attendance, created = EventAttendance.objects.get_or_create(event=event, student=student)

        if created:
            return JsonResponse({
                'status': 'success',
                'message': f"🎉 ENTRY GRANTED! Welcome {student.user.get_full_name()} ({student.student_id})",
                'student_name': student.user.get_full_name(),
                'student_id': student.student_id,
                'course': student.course,
                'time': attendance.entry_time.strftime("%I:%M %p")
            })
        else:
            return JsonResponse({
                'status': 'warning',
                'message': f"⚠️ ALREADY ENTERED! {student.user.get_full_name()} checked in earlier at {attendance.entry_time.strftime('%I:%M %p')}.",
                'student_name': student.user.get_full_name(),
                'student_id': student.student_id
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@login_required
def event_attendance_records(request, event_id):
    is_admin_user = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'is_admin', False)
    if not is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('event_list')

    event = get_object_or_404(Event, id=event_id)
    attendances = EventAttendance.objects.filter(event=event).select_related('student__user').order_by('-entry_time')
    registrations_count = EventRegistration.objects.filter(event=event).count()

    return render(request, 'events/attendance_records.html', {
        'event': event,
        'attendances': attendances,
        'registrations_count': registrations_count
    })
    
