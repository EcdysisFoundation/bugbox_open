
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0010_remove_application_measurement_model"),
    ]

    operations = [
        migrations.AddField(
            model_name='growerapplication',
            name='transect_1_latitude',
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text='Transect 1 latitude'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_1_longitude',
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text='Transect 1 longitude'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_2_latitude',
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text='Transect 2 latitude'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_2_longitude',
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text='Transect 2 longitude'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_3_latitude',
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text='Transect 3 latitude'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_3_longitude',
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text='Transect 3 longitude'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_4_latitude',
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text='Transect 4 latitude'
            ),
        ),
        migrations.AddField(
            model_name='growerapplication',
            name='transect_4_longitude',
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text='Transect 4 longitude'
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

