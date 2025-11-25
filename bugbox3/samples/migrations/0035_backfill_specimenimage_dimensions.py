from django.db import migrations
from django.core.files.storage import default_storage
from django.core.files.images import get_image_dimensions


def backfill_image_dimensions(apps, schema_editor):
    """
    Backfill image dimensions for existing SpecimenImage records.
    Reads dimensions from image files and stores them in the database.
    """
    SpecimenImage = apps.get_model('samples', 'SpecimenImage')
    
    batch_size = 100
    total = SpecimenImage.objects.count()
    processed = 0
    
    for start in range(0, total, batch_size):
        batch = SpecimenImage.objects.all()[start:start + batch_size]
        
        for specimen_image in batch:
            try:
                if specimen_image.image and hasattr(specimen_image.image, 'name') and specimen_image.image.name:
                    if default_storage.exists(specimen_image.image.name):
                        try:
                            dims = get_image_dimensions(specimen_image.image)
                            if dims and dims[0] and dims[1]:
                                specimen_image.image_width = dims[0]
                                specimen_image.image_height = dims[1]
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
                        except (OSError, IOError, ValueError) as e:
                            print(f"Warning: Could not read dimensions for thumbnail {specimen_image.image_thumbnail_large.name}: {e}")
                
                if (specimen_image.image_width is not None or 
                    specimen_image.image_height is not None or
                    specimen_image.image_thumbnail_large_width is not None or
                    specimen_image.image_thumbnail_large_height is not None):
                    specimen_image.save(update_fields=[
                        'image_width', 'image_height',
                        'image_thumbnail_large_width', 'image_thumbnail_large_height'
                    ])
                
                processed += 1
                if processed % 100 == 0:
                    print(f"Processed {processed}/{total} SpecimenImage records...")
                    
            except Exception as e:
                print(f"Error processing SpecimenImage {specimen_image.id}: {e}")
                continue
    
    print(f"Completed backfilling dimensions for {processed} SpecimenImage records.")


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
        ('samples', '0034_specimenimage_image_dimensions'),
    ]

    operations = [
        migrations.RunPython(backfill_image_dimensions, reverse_backfill)
    ]

