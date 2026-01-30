
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grower_portal', '0038_alter_csvimportfieldvalue_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='growersamplecodemapping',
            name='year_sampled',
            field=models.IntegerField(
                default=2024,
                help_text='Year the sample was taken (from application date_sampled or import prompt).'
            ),
            preserve_default=False,
        ),
    ]
