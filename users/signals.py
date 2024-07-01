from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

User = get_user_model()


@receiver(pre_delete, sender=User)
def prevent_superuser_delete(sender, instance, **kwargs):
    """Prevent deletion of superuser"""
    if instance.is_superuser:
        raise PermissionDenied("Superuser accounts cannot be deleted.")
