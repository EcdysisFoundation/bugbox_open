from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grower_portal', '0034_rename_to_sample_codes'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TransectCode',
            new_name='SampleCode',
        ),
        migrations.AlterField(
            model_name='sitetransect',
            name='site_code',
            field=models.ForeignKey(
                help_text='Parent site code',
                on_delete=models.CASCADE,
                related_name='transects',
                to='grower_portal.samplecode'
            ),
        ),
        migrations.RenameField(
            model_name='csvimportfieldvalue',
            old_name='transect_code',
            new_name='sample_code',
        ),
        migrations.AlterField(
            model_name='samplecode',
            name='used_in_application',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='used_sample_codes',
                to='grower_portal.growerapplication'
            ),
        ),
        migrations.AlterModelOptions(
            name='samplecode',
            options={
                'ordering': ['code'],
                'permissions': [('generate_sample_codes', 'Can generate sample codes')],
                'verbose_name': 'Sample Code',
                'verbose_name_plural': 'Sample Codes',
            },
        ),
    ]
