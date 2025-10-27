
from django.db import migrations


def populate_grazing_event_applications(apps, schema_editor):
    """Populate application field from application_measurement field"""
    GrazingEvent = apps.get_model('grower_portal', 'GrazingEvent')
    
    for grazing_event in GrazingEvent.objects.all():
        if hasattr(grazing_event, 'application_measurement') and grazing_event.application_measurement:
            grazing_event.application = grazing_event.application_measurement.application
            grazing_event.save()


def reverse_populate_grazing_event_applications(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0006_update_grazing_event_model"),
    ]

    operations = [
        migrations.RunPython(
            populate_grazing_event_applications,
            reverse_populate_grazing_event_applications
        ),
    ]
