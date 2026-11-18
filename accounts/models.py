from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_ADMIN = "admin"
    ROLE_STUDENT = "student"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_STUDENT, "Student"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    contact_number = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN
