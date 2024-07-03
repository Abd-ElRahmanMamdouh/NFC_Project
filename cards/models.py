import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

User = get_user_model()


class Product(models.Model):
    title = models.CharField("Title", max_length=500)
    price = models.DecimalField(
        "Price",
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Products"
        verbose_name_plural = "Products"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def get_related_objects(self):
        return self.product_groups.all()


class ProductGroup(models.Model):
    title = models.CharField("Title", max_length=500)
    price = models.DecimalField(
        "Price",
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    products = models.ManyToManyField(
        Product, blank=True, related_name="product_groups"
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Product Groups"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class NFCCard(models.Model):
    user = models.ForeignKey(
        User,
        related_name="user_cards",
        verbose_name="User",
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

    def get_absolute_url(self):
        return reverse('cards:landing_page', args=[self.uuid])


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
    card = models.OneToOneField(
        NFCCard,
        related_name="card_code",
        verbose_name="Card",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Purchasing Code"
        verbose_name_plural = "Purchasing Codes"
        ordering = ("-created_at",)

    def __str__(self):
        return self.code
