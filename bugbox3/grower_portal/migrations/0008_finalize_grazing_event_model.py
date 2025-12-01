
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0007_populate_grazing_event_applications"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grazingevent",
            name="application",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="grazing_events",
                to="grower_portal.growerapplication",
            ),
        ),
    ]
