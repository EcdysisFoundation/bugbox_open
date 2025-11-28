
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0009_add_grazing_event_unique_together"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ApplicationMeasurement",
        ),
    ]
