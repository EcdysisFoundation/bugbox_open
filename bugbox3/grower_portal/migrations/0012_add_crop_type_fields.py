
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0011_add_transect_coordinates_and_usage_tracking"),
    ]

    operations = [
        migrations.AddField(
            model_name="field",
            name="crop_type",
            field=models.CharField(
                max_length=100,
                blank=True,
                choices=[
                    ("row_crop", "Row crop"),
                    ("mixed_veg", "Mixed Vegetables/herbs/specialty crops/Hayfield"),
                ],
                help_text="Type of crop grown"
            ),
        ),
        migrations.AddField(
            model_name="field",
            name="crop_subtype",
            field=models.CharField(
                max_length=100,
                blank=True,
                choices=[
                    ("corn", "Corn"),
                    ("soybean", "Soybean"),
                    ("small_grain", "Small grain"),
                    ("potato", "Potato"),
                    ("peanut", "Peanut"),
                    ("other", "Other"),
                ],
                help_text="Specific crop subtype"
            ),
        ),
        migrations.AddField(
            model_name="field",
            name="crop_subtype_other",
            field=models.CharField(
                max_length=200,
                blank=True,
                help_text="Specify other crop type"
            ),
        ),
        migrations.AddField(
            model_name="field",
            name="small_grain_type",
            field=models.CharField(
                max_length=200,
                blank=True,
                help_text="Specify small grain type"
            ),
        ),
        migrations.AddField(
            model_name="field",
            name="uses_broad_fork",
            field=models.BooleanField(
                default=False,
                help_text="Uses broad fork cultivation"
            ),
        ),
        
        migrations.AddField(
            model_name="managementpractices",
            name="cover_crop_termination_other",
            field=models.CharField(
                max_length=200,
                blank=True,
                help_text="Specify other termination method"
            ),
        ),
        migrations.AddField(
            model_name="managementpractices",
            name="organic_amendment_other",
            field=models.CharField(
                max_length=200,
                blank=True,
                help_text="Specify other organic amendment type"
            ),
        ),
    ]