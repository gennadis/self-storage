# Generated by Django 4.0.5 on 2022-06-15 12:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0005_merge_20220615_1516'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lease',
            options={'verbose_name': 'Аренда', 'verbose_name_plural': 'Аренды'},
        ),
    ]