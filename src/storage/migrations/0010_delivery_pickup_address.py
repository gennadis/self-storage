# Generated by Django 4.0.5 on 2022-06-16 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0009_alter_lease_box"),
    ]

    operations = [
        migrations.AddField(
            model_name="delivery",
            name="pickup_address",
            field=models.CharField(
                db_index=True,
                default="None",
                max_length=150,
                verbose_name="Адрес забора груза",
            ),
            preserve_default=False,
        ),
    ]
