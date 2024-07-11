from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


PRODUCTS_CHOICES = [
    ("product1", "Product 1"),
    ("product2", "Product 2"),
    ("product3", "Product 3"),
    ("product4", "Product 4"),
]


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
    products = models.CharField(
        "Products", blank=True, null=True, max_length=500
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Product Groups"
        ordering = ("-created_at",)

    def get_products_display(self):
        if self.products:
            return ', '.join([dict(PRODUCTS_CHOICES).get(item, item) for item in self.products.split(',')])
        return ''

    def __str__(self):
        return self.title


class LinkDuration(models.Model):
    duration = models.PositiveIntegerField("Duration", default=1)

    class Meta:
        verbose_name = "Link Duration"
        verbose_name_plural = "Link Durations"
        ordering = ("-id",)

    def __str__(self):
        return str(self.duration)
