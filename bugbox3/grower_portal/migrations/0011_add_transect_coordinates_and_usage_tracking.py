
from django.contrib.gis.db.models import PointField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0010_remove_application_measurement_model"),
    ]

    operations = [
        migrations.AddField(
            model_name='growerapplication',
            name='transect_1_location',
            field=PointField(
                null=True,
                blank=True,
                srid=4326,
                help_text='Transect 1 GPS location (longitude, latitude)'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_2_location',
            field=PointField(
                null=True,
                blank=True,
                srid=4326,
                help_text='Transect 2 GPS location (longitude, latitude)'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_3_location',
            field=PointField(
                null=True,
                blank=True,
                srid=4326,
                help_text='Transect 3 GPS location (longitude, latitude)'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_4_location',
            field=PointField(
                null=True,
                blank=True,
                srid=4326,
                help_text='Transect 4 GPS location (longitude, latitude)'
            ),
        ),
        migrations.AddField(
            model_name='transectcode',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='transectcode',
            name='used_in_application',
            field=models.ForeignKey(
                'GrowerApplication',
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                related_name='used_transect_codes'
            ),
        ),
        migrations.AddField(
            model_name='transectcode',
            name='used_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]

