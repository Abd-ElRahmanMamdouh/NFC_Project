from django.contrib.auth import get_user_model
from django.db import models
import uuid
from services.models import Product, ProductGroup

User = get_user_model()


class PurchasingCode(models.Model):
    code = models.CharField(
        "Purchasing Code",
        blank=True,
        null=True,
        unique=True,
        max_length=120,
        help_text="automatically generated",
    )
    password = models.CharField(
        "Password",
        blank=True,
        null=True,
        max_length=120,
        help_text="automatically generated",
    )
    group = models.ForeignKey(
        ProductGroup,
        related_name="group_codes",
        verbose_name="Group",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    extra_products = models.ManyToManyField(
        Product, blank=True, related_name="product_codes", verbose_name="Extra Products"
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Purchasing Code"
        verbose_name_plural = "Purchasing Codes"
        ordering = ("-created_at",)

    def __str__(self):
        return self.code


class NFCCard(models.Model):
    user = models.ForeignKey(
        User,
        related_name="user_cards",
        verbose_name="User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    code = models.OneToOneField(
        PurchasingCode,
        related_name="code_cards",
        verbose_name="Code",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "NFC Card"
        verbose_name_plural = "NFC Cards"
        ordering = ("-created_at",)

    def __str__(self):
        return str(self.uuid)
