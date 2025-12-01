
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("samples", "0033_multispecimenimage_label_image_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="specimenimage",
            name="image_width",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="specimenimage",
            name="image_height",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="specimenimage",
            name="image_thumbnail_large_width",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="specimenimage",
            name="image_thumbnail_large_height",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]



