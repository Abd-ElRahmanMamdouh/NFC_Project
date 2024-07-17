# Generated by Django 4.2 on 2024-07-17 19:31

from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cards", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CodeBatchArchived",
            fields=[],
            options={
                "verbose_name": "Code Archive",
                "verbose_name_plural": "Code Archive",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cards.codebatch",),
        ),
        migrations.CreateModel(
            name="URLBatchArchived",
            fields=[],
            options={
                "verbose_name": "URL Archive",
                "verbose_name_plural": "URL Archive",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cards.urlbatch",),
        ),
    ]
