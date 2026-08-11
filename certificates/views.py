import qrcode
import io
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from students.models import StudentProfile
from .models import Certificate

@login_required
def certificate_list(request):
    user = request.user
    is_admin_user = user.is_superuser or user.is_staff or getattr(user, 'is_admin', False)

    if is_admin_user:
        certificates = Certificate.objects.select_related('student__user').all().order_by('-issue_date')
    else:
        if hasattr(user, 'student_profile'):
            certificates = Certificate.objects.filter(student=user.student_profile).order_by('-issue_date')
        else:
            certificates = []

    return render(request, 'certificates/certificate_list.html', {'certificates': certificates, 'is_admin': is_admin_user})


@login_required
def issue_certificate(request):
    is_admin_user = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'is_admin', False)
    if not is_admin_user:
        messages.error(request, "Access denied. Admin permissions required.")
        return redirect('certificate_list')

    students = StudentProfile.objects.select_related('user').all()

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        title = request.POST.get('title')
        certificate_type = request.POST.get('certificate_type')
        description = request.POST.get('description')

        student = get_object_or_404(StudentProfile, id=student_id)

        cert = Certificate.objects.create(
            student=student,
            title=title,
            certificate_type=certificate_type,
            description=description
        )

        messages.success(request, f"🎓 Certificate issued successfully to {student.user.get_full_name()}! ID: {cert.certificate_id}")
        return redirect('certificate_list')

    return render(request, 'certificates/issue_certificate.html', {'students': students})


@login_required
def view_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, certificate_id=certificate_id)

    # Generate Verification QR Code
    qr_content = f"VERIFIED_CERTIFICATE:{cert.certificate_id}:{cert.student.student_id}"
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#5C061C", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'cert': cert,
        'qr_b64': qr_b64,
    }
    return render(request, 'certificates/view_certificate.html', context)