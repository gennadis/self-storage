# Generated by Django 4.0.5 on 2022-06-17 19:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0013_alter_delivery_comment_alter_delivery_courier_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lease",
            name="created_on",
            field=models.DateField(
                default=django.utils.timezone.now, verbose_name="Дата создания"
            ),
        ),
        migrations.AlterField(
            model_name="lease",
            name="expires_on",
            field=models.DateField(verbose_name="Дата окончания аренды"),
        ),
        migrations.AlterField(
            model_name="lease",
            name="paid_on",
            field=models.DateField(
                blank=True, db_index=True, null=True, verbose_name="Дата оплаты"
            ),
        ),
    ]
