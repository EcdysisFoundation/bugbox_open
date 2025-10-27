
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0005_field_acres_sampled_field_is_confined_dairy_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="grazingevent",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="grazingevent",
            name="application",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="grazing_events",
                to="grower_portal.growerapplication",
            ),
        ),
        migrations.RemoveField(
            model_name="grazingevent",
            name="application_measurement",
        ),
        migrations.AlterModelOptions(
            name="grazingevent",
            options={
                "ordering": ["application", "event_number"],
                "verbose_name": "Grazing Event",
                "verbose_name_plural": "Grazing Events",
            },
        ),
    ]
