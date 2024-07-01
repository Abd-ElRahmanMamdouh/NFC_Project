import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


ROLE_CHOICES = [
    ("admin", "Admin User"),
    ("regular", "Regular User"),
]


class CustomUser(AbstractUser):
    role = models.CharField(
        "Role", choices=ROLE_CHOICES, max_length=50, default="regular"
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

    @property
    def user_admin(self):
        if self.role == "admin":
            return True
        return False


class AuthToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.user.username
