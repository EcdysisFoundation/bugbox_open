from django.db import migrations


def create_entries(apps, schema_editor):

    AiTraining = apps.get_model('taxonomy', 'AiTraining')

    recs = AiTraining.objects.values('id', 'model__entered_date')
    for r in recs:
        AiTraining.objects.filter(id=r['id']).update(
            entered_date=r['model__entered_date']
        )


class Migration(migrations.Migration):
    dependencies = [
        ('taxonomy', '0007_aitraining_entered_date'),
    ]

    operations = [
        migrations.RunPython(create_entries)
    ]
