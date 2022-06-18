# Generated by Django 4.0.5 on 2022-06-16 06:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storage', '0007_alter_box_depth_alter_box_length_alter_box_width'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_status', models.CharField(choices=[('Unprocessed', 'Курьер не назначен'), ('In_process', 'Курьер в пути'), ('Completed', 'Груз на складе')], db_index=True, default='Unprocessed', max_length=15, verbose_name='Статус доставки заказа')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('registered_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Время назначения курьера')),
                ('delivered_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Время доставки груза')),
                ('courier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courier', to=settings.AUTH_USER_MODEL, verbose_name='Курьер')),
                ('lease', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lease', to='storage.lease', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Заказ на доставку',
                'verbose_name_plural': 'Заказы на доставку',
            },
        ),
    ]