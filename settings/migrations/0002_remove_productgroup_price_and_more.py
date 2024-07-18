# Generated by Django 4.2 on 2024-07-18 10:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("settings", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="productgroup",
            name="price",
        ),
        migrations.AlterField(
            model_name="linkduration",
            name="duration",
            field=models.PositiveIntegerField(
                default=1, verbose_name="Duration in Years"
            ),
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="products",
            field=models.CharField(
                default="product1", max_length=500, verbose_name="Products"
            ),
            preserve_default=False,
        ),
    ]
