from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Role Identity Flags (Admin vs Student)
    is_admin = models.BooleanField(default=False, verbose_name="Is Admin/Faculty")
    is_student = models.BooleanField(default=False, verbose_name="Is Student")

    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        role = "Admin" if self.is_admin else ("Student" if self.is_student else "User")
        return f"{self.username} ({role})"