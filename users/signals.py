from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models.signals import post_delete, pre_delete, pre_save
from django.dispatch.dispatcher import receiver

User = get_user_model()


@receiver(pre_delete, sender=User)
def prevent_superuser_delete(sender, instance, **kwargs):
    """Prevent deletion of superuser"""
    if instance.is_superuser:
        raise PermissionDenied("Superuser accounts cannot be deleted.")


@receiver(pre_save, sender=User)
def delete_image_onchange(sender, instance, **kwargs):
    """Delete image file from server On change instance"""
    try:
        obj = instance.__class__.objects.get(id=instance.id)
        if obj.image:
            old_img = obj.image.path
            new_img = instance.image.path
        else:
            old_img = None
            new_img = None
        if new_img != old_img:
            import os

            if os.path.exists(old_img):
                os.remove(old_img)
    except instance.__class__.DoesNotExist:
        pass


@receiver(post_delete, sender=User)
def delete_image_ondelete(sender, instance, **kwargs):
    """Delete image file from server On delete instance"""
    instance.image.delete(False)
