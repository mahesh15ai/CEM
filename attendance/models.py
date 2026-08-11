from django.db import models
from students.models import StudentProfile

class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present')
    marked_by = models.CharField(max_length=100, default='System Scanner')

    class Meta:
        ordering = ['-date', '-time']
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.student_id} - {self.date} ({self.status})"