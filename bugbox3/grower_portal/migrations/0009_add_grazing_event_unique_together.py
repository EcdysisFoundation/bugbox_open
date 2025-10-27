
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0008_finalize_grazing_event_model"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="grazingevent",
            unique_together={("application", "event_number")},
        ),
    ]
