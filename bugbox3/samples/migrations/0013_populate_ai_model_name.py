from django.db import migrations


def create_entries(apps, schema_editor):

    Specimen = apps.get_model('samples', 'Specimen')

    recs = Specimen.objects.filter(
        ai_version__isnull=False).values('id', 'ai_version__version')
    for r in recs:
        Specimen.objects.filter(id=r['id']).update(
            ai_model_name=r['ai_version__version']
        )


class Migration(migrations.Migration):
    dependencies = [
        ('samples', '0012_specimen_ai_model_name'),
    ]

    operations = [
        migrations.RunPython(create_entries)
    ]
