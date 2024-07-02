from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver

from core.utils import unique_code_generator, unique_password_generator

from .models import PurchasingCode


@receiver(pre_save, sender=PurchasingCode)
def pre_save_code(sender, instance, *args, **kwargs):
    if not instance.code:
        instance.code = unique_code_generator(instance)
    if not instance.password:
        instance.password = unique_password_generator(instance)
