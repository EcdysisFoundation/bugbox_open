
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0003_add_insecticide_comments"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicationmeasurement",
            name="transect_latitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                help_text="Transect latitude (-90 to 90) - specific location where this transect was sampled",
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-90),
                    django.core.validators.MaxValueValidator(90),
                ],
            ),
        ),
        migrations.AddField(
            model_name="applicationmeasurement",
            name="transect_longitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                help_text="Transect longitude (-180 to 180) - specific location where this transect was sampled",
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-180),
                    django.core.validators.MaxValueValidator(180),
                ],
            ),
        ),
    ]
