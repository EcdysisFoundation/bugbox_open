# Generated migration for creating GrowerSampleCodeMapping model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grower_portal', '0036_add_location_fields_to_growerprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrowerSampleCodeMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('grower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sample_code_mappings', to=settings.AUTH_USER_MODEL)),
                ('sample_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grower_mappings', to='grower_portal.samplecode')),
            ],
            options={
                'verbose_name': 'Grower Sample Code Mapping',
                'verbose_name_plural': 'Grower Sample Code Mappings',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='growersamplecodemapping',
            unique_together={('grower', 'sample_code')},
        ),
    ]
