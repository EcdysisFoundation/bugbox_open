# Generated migration for adding location fields to GrowerProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grower_portal', '0035_rename_transectcode_to_samplecode'),
    ]

    operations = [
        migrations.AddField(
            model_name='growerprofile',
            name='state',
            field=models.CharField(blank=True, help_text='State or province', max_length=100),
        ),
        migrations.AddField(
            model_name='growerprofile',
            name='city',
            field=models.CharField(blank=True, help_text='City', max_length=200),
        ),
        migrations.AddField(
            model_name='growerprofile',
            name='county',
            field=models.CharField(blank=True, help_text='County', max_length=200),
        ),
        migrations.AddField(
            model_name='growerprofile',
            name='country',
            field=models.CharField(blank=True, help_text='Country', max_length=100),
        ),
    ]
