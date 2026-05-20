
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grower_portal', '0044_labelgeneration_async_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BirdRecordingUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year_sampled', models.IntegerField(help_text='Year from GrowerSampleCodeMapping, used in the S3 path.')),
                ('s3_key', models.CharField(max_length=512)),
                ('original_filename', models.CharField(max_length=255)),
                ('content_type', models.CharField(max_length=128)),
                ('file_size_bytes', models.BigIntegerField()),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
                    default='pending',
                    max_length=20,
                )),
                ('uploaded_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('grower', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bird_recording_uploads',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('sample_code', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='bird_recording_uploads',
                    to='grower_portal.samplecode',
                )),
            ],
            options={
                'verbose_name': 'Bird recording upload',
                'verbose_name_plural': 'Bird recording uploads',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='birdrecordingupload',
            index=models.Index(fields=['grower', '-created_at'], name='grower_port_grower__a8f2c1_idx'),
        ),
        migrations.AddIndex(
            model_name='birdrecordingupload',
            index=models.Index(fields=['sample_code', '-created_at'], name='grower_port_sample__4e7b2a_idx'),
        ),
        migrations.AddIndex(
            model_name='birdrecordingupload',
            index=models.Index(fields=['status'], name='grower_port_status_91c4d0_idx'),
        ),
    ]
