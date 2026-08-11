import qrcode
from io import BytesIO
from datetime import timedelta
from django.core.files import File
from django.db import models
from accounts.models import User

class StudentProfile(models.Model):
    # ... existing choices and fields ...
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, default='Computer Science & IT')
    course = models.CharField(max_length=50, default='BCA')
    year = models.CharField(max_length=50, default='Third Year')
    division = models.CharField(max_length=10, default='A')
    roll_number = models.IntegerField()
    dob = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='students/photos/', default='students/default.png')
    qr_code = models.ImageField(upload_to='students/qr/', blank=True, null=True)
    
    # Registration Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

    @property
    def valid_until(self):
        """Calculates exact date 1 year from registration day"""
        if self.created_at:
            return self.created_at.date() + timedelta(days=365)
        return None

    @property
    def academic_session(self):
        """Generates dynamic session e.g. 2026-27 based on registration year"""
        if self.created_at:
            start_year = self.created_at.year
            end_year = str(start_year + 1)[-2:]
            return f"{start_year}-{end_year}"
        return "2026-27"

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr_text = f"STUDENT:{self.student_id}"
            qr_img = qrcode.make(qr_text)
            
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            file_name = f"qr_{self.student_id}.png"
            self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)