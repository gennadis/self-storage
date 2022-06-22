import random

from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandError, CommandParser

from storage.models import Box, Warehouse


class Command(BaseCommand):
    help = "Generate random boxes for existing warehouses"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(f"Flushing box table."))

        Box.objects.all().delete()

        min_box_amount = 100
        max_box_amount = 250

        min_floor = min_length = min_width = min_depth = 1
        max_length = 8
        max_area_sqm = 16
        max_depth = 4
        max_floor = 4
        min_price_per_sqm = 400
        max_price_per_sqm = 800

        for warehouse in Warehouse.objects.all().iterator():
            self.stdout.write(f"Generating boxes for warehouse '{warehouse}'.")

            new_boxes = []
            for box_index in range(1, random.randint(min_box_amount, max_box_amount)):
                length_m = random.randint(min_length, max_length)
                area_sqm = random.randint(length_m, max_area_sqm)
                width_m = max(min_width, int(area_sqm / length_m))
                rate = random.randint(min_price_per_sqm, max_price_per_sqm) * area_sqm

                new_boxes.append(
                    Box(
                        code=f"{warehouse.id:>02d}-{box_index:>04d}",
                        warehouse=warehouse,
                        floor=random.randint(min_floor, max_floor),
                        length=length_m * 100,
                        width=width_m * 100,
                        depth=random.randint(min_depth, max_depth) * 100,
                        monthly_rate=rate,
                    )
                )

            self.stdout.write(f"Created {len(new_boxes)}. Inserting into DB.")

            Box.objects.bulk_create(new_boxes)

            self.stdout.write(f"Done.")

        self.stdout.write(self.style.SUCCESS(f"Finished generating boxes."))
