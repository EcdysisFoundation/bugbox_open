
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0014_remove_crop_variety_field"),
    ]

    operations = [
        migrations.AlterField(
            model_name="field",
            name="crop_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("row_crop", "Row crop"),
                    ("mixed_veg", "Mixed Vegetables/herbs/specialty crops"),
                    ("hayfield", "Hayfield"),
                ],
                help_text="Type of crop grown",
                max_length=100,
            ),
        ),
    ]

