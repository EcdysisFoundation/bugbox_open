
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrate_existing_transect_codes(apps, schema_editor):
    """Set project_type='avalanche' for all existing transect codes"""
    TransectCode = apps.get_model('grower_portal', 'TransectCode')
    LabelGeneration = apps.get_model('grower_portal', 'LabelGeneration')
    
    for tc_data in TransectCode.objects.values('id', 'code'):
        tc = TransectCode.objects.get(id=tc_data['id'])
        tc.project_type = 'avalanche'
        
        label_gen = LabelGeneration.objects.filter(
            transect_codes_generated__contains=[tc_data['code']]
        ).first()
        
        if label_gen:
            tc.cluster_number = label_gen.cluster_number
            tc.year = label_gen.year
        
        tc.save()


def reverse_migrate_codes(apps, schema_editor):
    """Reverse migration - not needed"""


class Migration(migrations.Migration):

    dependencies = [
        ('grower_portal', '0031_admin_application_creation_consolidated'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transectcode',
            options={
                'ordering': ['id'],
                'permissions': [('generate_transect_codes', 'Can generate transect codes')],
                'verbose_name': 'Transect Code',
                'verbose_name_plural': 'Transect Codes'
            },
        ),
        migrations.RenameField(
            model_name='transectcode',
            old_name='transect_code',
            new_name='code',
        ),
        migrations.AddField(
            model_name='transectcode',
            name='project_type',
            field=models.CharField(
                choices=[('avalanche', 'Avalanche'), ('ignite', 'Ignite')],
                default='avalanche',
                help_text='Project type: Avalanche or Ignite',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='transectcode',
            name='cluster_number',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Cluster identifier',
                max_length=10
            ),
        ),
        migrations.AddField(
            model_name='transectcode',
            name='year',
            field=models.IntegerField(
                blank=True,
                help_text='Year for the labels',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='transectcode',
            name='site_code_numeric',
            field=models.IntegerField(
                blank=True,
                help_text='Numeric site code for Ignite project (e.g., 5001)',
                null=True
            ),
        ),
        migrations.RunPython(migrate_existing_transect_codes, reverse_migrate_codes),
        migrations.CreateModel(
            name='SiteTransect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transect_number', models.IntegerField(
                    help_text='Transect number (1-4)',
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(4)
                    ]
                )),
                ('is_active', models.BooleanField(default=True)),
                ('is_used', models.BooleanField(default=False)),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('site_code', models.ForeignKey(
                    help_text='Parent site code',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='transects',
                    to='grower_portal.transectcode'
                )),
            ],
            options={
                'verbose_name': 'Site Transect',
                'verbose_name_plural': 'Site Transects',
                'ordering': ['site_code', 'transect_number'],
                'unique_together': {('site_code', 'transect_number')},
            },
        ),
        migrations.AlterModelOptions(
            name='transectcode',
            options={
                'ordering': ['code'],
                'permissions': [('generate_transect_codes', 'Can generate transect codes')],
                'verbose_name': 'Transect Code',
                'verbose_name_plural': 'Transect Codes'
            },
        ),
    ]
