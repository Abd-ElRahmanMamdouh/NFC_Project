from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db.models.signals import (post_delete, post_save, pre_delete,
                                      pre_save)
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


@receiver(post_save, sender=User)
def assign_permissions(sender, instance, **kwargs):
    user = instance
    role = user.role

    permissions = []

    if role == "superuser":
        user.is_staff = True
        user.is_superuser = True
    elif role == "url":
        user.is_staff = True
        permissions = [
            'add_nfccard',
            'change_nfccard',
            'view_nfccard',
        ]
    elif role == "artist":
        user.is_staff = True
        permissions = [
            'add_nfccard',
            'change_nfccard',
            'view_nfccard',
            'add_purchasingcode',
            'change_purchasingcode',
            'view_purchasingcode',
        ]
    elif role == "administrator":
        user.is_staff = True
        permissions = [
            'add_codebatch',
            'change_codebatch',
            'delete_codebatch',
            'view_codebatch',
            'add_urlbatch',
            'change_urlbatch',
            'delete_urlbatch',
            'view_urlbatch',
        ]
    elif role == "customer":
        user.is_staff = False

    user.user_permissions.clear()

    for perm in permissions:
        try:
            permission = Permission.objects.get(codename=perm)
            user.user_permissions.add(permission)
        except Permission.DoesNotExist:
            pass
