from django.db import models

# Create your models here.
import uuid
from django.db import models
from students.models import StudentProfile

class Certificate(models.Model):
    CERT_TYPES = (
        ('Event Participation', 'Event Participation'),
        ('Academic Excellence', 'Academic Excellence'),
        ('Course Completion', 'Course Completion'),
        ('Sports & Extra Curricular', 'Sports & Extra Curricular'),
    )

    certificate_id = models.CharField(max_length=50, unique=True, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=200)
    certificate_type = models.CharField(max_length=50, choices=CERT_TYPES, default='Event Participation')
    description = models.TextField(blank=True, null=True)
    issue_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"VBM-CERT-2026-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.certificate_id} - {self.student.user.get_full_name()}"