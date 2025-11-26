from django.db import migrations
from django.core.files.storage import default_storage
from django.core.files.images import get_image_dimensions
from django.conf import settings


def backfill_image_dimensions_resumable(apps, schema_editor):
    return
    
    SpecimenImage = apps.get_model('samples', 'SpecimenImage')
    
    records_to_process = SpecimenImage.objects.filter(
        image_width__isnull=True,
        image_height__isnull=True
    )
    
    total = records_to_process.count()
    if total == 0:
        print("All records already have dimensions. Nothing to process.")
        return
    
    batch_size = 500
    processed = 0
    updated = 0
    
    for start in range(0, total, batch_size):
        batch = records_to_process[start:start + batch_size]
        
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
                            print(f"Warning: Could not read dimensions for image {specimen_image.image.name}: {e}")
                
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
                            print(f"Warning: Could not read dimensions for thumbnail {specimen_image.image_thumbnail_large.name}: {e}")
                
                if needs_save:
                    specimen_image.save(update_fields=[
                        'image_width', 'image_height',
                        'image_thumbnail_large_width', 'image_thumbnail_large_height'
                    ])
                    updated += 1
                
                processed += 1
                if processed % 500 == 0:
                    print(f"Processed {processed}/{total} SpecimenImage records ({updated} updated)...")
                    
            except Exception as e:
                print(f"Error processing SpecimenImage {specimen_image.id}: {e}")
                continue
    
    print(f"Completed: processed {processed} records, updated {updated} records with dimensions.")


def reverse_backfill(apps, schema_editor):
    """
    Reverse migration: clear the dimension fields.
    """
    SpecimenImage = apps.get_model('samples', 'SpecimenImage')
    SpecimenImage.objects.all().update(
        image_width=None,
        image_height=None,
        image_thumbnail_large_width=None,
        image_thumbnail_large_height=None
    )


class Migration(migrations.Migration):
    dependencies = [
        ('samples', '0035_backfill_specimenimage_dimensions'),
    ]

    operations = [
        migrations.RunPython(backfill_image_dimensions_resumable, reverse_backfill)
    ]

