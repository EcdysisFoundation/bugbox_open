
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0015_update_crop_type_choices_separate_hayfield"),
    ]

    operations = [
        migrations.AddField(
            model_name="field",
            name="crop_varieties",
            field=models.CharField(
                blank=True,
                help_text="Crop variety or varieties grown (for orchards)",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="managementpractices",
            name="grazer_types_other",
            field=models.CharField(
                blank=True, 
                help_text="Specify other grazer type", 
                max_length=200
            ),
        ),
        migrations.AddField(
            model_name="managementpractices",
            name="ground_cover_management_other",
            field=models.CharField(
                blank=True,
                help_text="Specify other ground cover management method",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="managementpractices",
            name="grazer_types",
            field=models.CharField(
                blank=True,
                choices=[
                    ("cattle", "Cattle"),
                    ("sheep", "Sheep"),
                    ("goats", "Goats"),
                    ("hogs", "Hogs"),
                    ("chickens", "Chickens"),
                    ("other", "Other"),
                ],
                help_text="Type of animals used for grazing",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="managementpractices",
            name="ground_cover_management",
            field=models.CharField(
                blank=True,
                choices=[
                    ("grazing", "Grazing"),
                    ("mowing", "Mowing"),
                    ("tilling", "Tilling"),
                    ("herbicide", "Herbicide"),
                    ("other", "Other"),
                ],
                help_text="Method used to manage ground cover",
                max_length=100,
            ),
        ),
    ]

