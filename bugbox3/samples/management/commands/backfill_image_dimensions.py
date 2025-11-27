from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.images import get_image_dimensions
from bugbox3.samples.models import SpecimenImage
import gc


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        limit = options['limit']
        
        queryset = SpecimenImage.objects.filter(
            image_width__isnull=True,
            image_height__isnull=True
        )
        
        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('All records already have dimensions. Nothing to process.'))
            return
        
        if limit:
            queryset = queryset[:limit]
            total = min(total, limit)
        
        self.stdout.write(f'Found {total} records missing dimensions. Starting backfill...')
        
        processed = 0
        updated = 0
        errors = 0
        
        for start in range(0, total, batch_size):
            batch = queryset[start:start + batch_size]
            
            for specimen_image in batch:
                try:
                    needs_save = False
                    
                    if specimen_image.image and hasattr(specimen_image.image, 'name') and specimen_image.image.name:
                        if default_storage.exists(specimen_image.image.name):
                            try:
                                dims = get_image_dimensions(specimen_image.image)
                                if dims and dims[0] and dims[1]:
                                    specimen_image.image_width = dims[0]
                                    specimen_image.image_height = dims[1]
                                    needs_save = True
                            except (OSError, IOError, ValueError) as e:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'Could not read dimensions for image {specimen_image.image.name}: {e}'
                                    )
                                )
                    
                    if (specimen_image.image_thumbnail_large and 
                        hasattr(specimen_image.image_thumbnail_large, 'name') and 
                        specimen_image.image_thumbnail_large.name):
                        if default_storage.exists(specimen_image.image_thumbnail_large.name):
                            try:
                                thumb_dims = get_image_dimensions(specimen_image.image_thumbnail_large)
                                if thumb_dims and thumb_dims[0] and thumb_dims[1]:
                                    specimen_image.image_thumbnail_large_width = thumb_dims[0]
                                    specimen_image.image_thumbnail_large_height = thumb_dims[1]
                                    needs_save = True
                            except (OSError, IOError, ValueError) as e:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'Could not read dimensions for thumbnail {specimen_image.image_thumbnail_large.name}: {e}'
                                    )
                                )
                    
                    if needs_save:
                        specimen_image.save(update_fields=[
                            'image_width', 'image_height',
                            'image_thumbnail_large_width', 'image_thumbnail_large_height'
                        ])
                        updated += 1
                    
                    processed += 1
                    if processed % 500 == 0:
                        self.stdout.write(f'Processed {processed}/{total} records ({updated} updated, {errors} errors)...')
                        gc.collect()
                        
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error processing SpecimenImage {specimen_image.id}: {e}')
                    )
                    continue
            
            gc.collect()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Completed: processed {processed} records, updated {updated} records with dimensions, {errors} errors.'
            )
        )

