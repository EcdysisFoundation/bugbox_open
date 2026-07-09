from django.db import migrations, models

import bugbox3.grower_portal.constants as constants


class Migration(migrations.Migration):

    dependencies = [
        ('grower_portal', '0049_alter_csvimportlog_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='grazingeventanimal',
            name='average_weight_unit',
            field=models.CharField(
                choices=constants.WEIGHT_UNIT_CHOICES,
                default=constants.DEFAULT_WEIGHT_UNIT,
                help_text='Unit used when entering average weight',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='grazingeventanimal',
            name='duration_unit',
            field=models.CharField(
                choices=constants.TIME_UNIT_CHOICES,
                default=constants.DEFAULT_TIME_UNIT,
                help_text='Unit used when entering grazing duration',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='grazingeventanimal',
            name='rest_period_unit',
            field=models.CharField(
                choices=constants.TIME_UNIT_CHOICES,
                default=constants.DEFAULT_TIME_UNIT,
                help_text='Unit used when entering rest period',
                max_length=10,
            ),
        ),
    ]
