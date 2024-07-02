from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


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
        verbose_name_plural = "Groups"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title
