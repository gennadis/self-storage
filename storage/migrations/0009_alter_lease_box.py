# Generated by Django 4.0.5 on 2022-06-16 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0008_delivery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lease',
            name='box',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leases', to='storage.box', verbose_name='Бокс'),
        ),
    ]
