from django.db import migrations


def create_entries(apps, schema_editor):

    AiTraining = apps.get_model('taxonomy', 'AiTraining')

    recs = AiTraining.objects.values('id', 'model__version')
    for r in recs:
        AiTraining.objects.filter(id=r['id']).update(
            model_name=r['model__version']
        )


class Migration(migrations.Migration):
    dependencies = [
        ('taxonomy', '0005_alter_aitraining_model'),
    ]

    operations = [
        migrations.RunPython(create_entries)
    ]
