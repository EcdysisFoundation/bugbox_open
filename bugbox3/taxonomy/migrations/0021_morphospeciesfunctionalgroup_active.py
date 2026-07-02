from django.db import migrations, models


def migrate_weight_to_active(apps, schema_editor):
    MorphospeciesFunctionalGroup = apps.get_model('taxonomy', 'MorphospeciesFunctionalGroup')
    MorphospeciesFunctionalGroup.objects.filter(weight__lte=0).delete()
    MorphospeciesFunctionalGroup.objects.filter(weight__gt=0).update(active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0020_morphospeciesfunctionalgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='morphospeciesfunctionalgroup',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(migrate_weight_to_active, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='morphospeciesfunctionalgroup',
            name='weight',
        ),
    ]
