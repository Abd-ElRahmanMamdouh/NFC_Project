# Generated by Django 4.2 on 2024-07-03 19:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cards", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nfccard",
            name="uuid",
            field=models.UUIDField(default="", editable=False, unique=True),
        ),
    ]