# Generated by Django 4.2 on 2024-07-17 19:31

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LinkDuration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "duration",
                    models.PositiveIntegerField(default=1, verbose_name="Duration"),
                ),
            ],
            options={
                "verbose_name": "Link Duration",
                "verbose_name_plural": "Link Durations",
                "ordering": ("-id",),
            },
        ),
        migrations.CreateModel(
            name="ProductGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=500, verbose_name="Title")),
                (
                    "price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.00"))
                        ],
                        verbose_name="Price",
                    ),
                ),
                (
                    "products",
                    models.CharField(
                        blank=True, max_length=500, null=True, verbose_name="Products"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
            ],
            options={
                "verbose_name": "Group",
                "verbose_name_plural": "Product Groups",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="CRUDLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("CREATE", "Created"),
                            ("UPDATE", "Updated"),
                            ("DELETE", "Deleted"),
                        ],
                        max_length=10,
                    ),
                ),
                ("object_name", models.CharField(max_length=100)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Log",
                "verbose_name_plural": "Logs",
                "ordering": ("-timestamp",),
            },
        ),
    ]
