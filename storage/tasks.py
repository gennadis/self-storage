from .models import Warehouse

from celery import shared_task


@shared_task
def count_warehouses():
    return Warehouse.objects.count()


@shared_task
def rename_widget(warehouse_id, address):
    warehouse = Warehouse.objects.get(id=warehouse_id)
    warehouse.address = address
    warehouse.save()
