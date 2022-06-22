from io import BytesIO
from urllib.parse import urlsplit

import requests
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandError, CommandParser

from storage.models import Warehouse, WarehouseImage


class Command(BaseCommand):
    help = "Load, parse JSON data of warehouses and populate DB"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("url")

    def handle(self, *args, **options):
        self.stdout.write("Loading JSON with warehouses from remote address.")

        response = requests.get(options["url"])
        response.raise_for_status()
        warehouses_data = response.json()

        self.stdout.write(
            self.style.WARNING("Flushing Warehouse and WarehouseImage tables.")
        )

        Warehouse.objects.all().delete()
        WarehouseImage.objects.all().delete()

        for warehouse in warehouses_data.get("warehouses"):

            new_warehouse = Warehouse(
                city=warehouse.get("city"),
                address=warehouse.get("address"),
                description=warehouse.get("description"),
                thumbnail=warehouse.get("thumbnail"),
                contact_phone=warehouse.get("contact_phone"),
                temperature=warehouse.get("temperature"),
                ceiling_height=warehouse.get("ceiling_height"),
            )
            try:
                new_warehouse.full_clean()
            except ValidationError as err:
                raise CommandError(
                    "New warehouse object failed validation", err.message_dict
                )

            new_warehouse.save()
            self.stdout.write(
                f"Warehouse on '{new_warehouse}' successfully added to DB"
            )

            for index, img_url in enumerate(warehouse.get("images")):
                self.stdout.write("Loading images for warehouse...")

                img_filename = urlsplit(img_url).path.split("/")[-1]

                try:
                    response = requests.get(img_url)
                    response.raise_for_status()
                except requests.HTTPError as err:
                    self.style.WARNING(f"Failed to fetch image {img_url}")
                    self.style.WARNING(err)
                    continue

                img_file = ImageFile(BytesIO(response.content))

                new_image = new_warehouse.images.create()
                new_image.image_file.save(img_filename, img_file, save=False)
                new_image.index = index + 1
                new_image.save()

            self.stdout.write("Finished loading images for warehouse.")

        self.stdout.write(self.style.SUCCESS("Finished loading warehouses."))
