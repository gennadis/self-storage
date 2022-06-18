# Generated by Django 4.0.5 on 2022-06-15 11:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0003_advertisingcompany"),
    ]

    operations = [
        migrations.CreateModel(
            name="Link",
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
                    "advertising_company",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="link",
                        to="storage.advertisingcompany",
                        verbose_name="Рекламная компания",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ссылка",
                "verbose_name_plural": "Ссылки",
            },
        ),
    ]
