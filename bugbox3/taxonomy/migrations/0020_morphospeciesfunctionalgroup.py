from django.db import migrations, models
import django.db.models.deletion


def migrate_m2m_to_through(apps, schema_editor):
    Morphospecies = apps.get_model('taxonomy', 'Morphospecies')
    MorphospeciesFunctionalGroup = apps.get_model('taxonomy', 'MorphospeciesFunctionalGroup')
    through_rows = []
    for morpho in Morphospecies.objects.all():
        for fg in morpho.functional_groups.all():
            through_rows.append(
                MorphospeciesFunctionalGroup(
                    morphospecies_id=morpho.id,
                    functional_group_id=fg.id,
                    weight=1.0,
                )
            )
    if through_rows:
        MorphospeciesFunctionalGroup.objects.bulk_create(through_rows, ignore_conflicts=True)


def reverse_migrate_through_to_m2m(apps, schema_editor):
    Morphospecies = apps.get_model('taxonomy', 'Morphospecies')
    MorphospeciesFunctionalGroup = apps.get_model('taxonomy', 'MorphospeciesFunctionalGroup')
    for row in MorphospeciesFunctionalGroup.objects.select_related('morphospecies', 'functional_group'):
        row.morphospecies.functional_groups.add(row.functional_group)


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0019_rename_taxonomy_unable_to_taxonomy_reviewed'),
    ]

    operations = [
        migrations.CreateModel(
            name='MorphospeciesFunctionalGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField()),
                (
                    'functional_group',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taxonomy.functionalgroup'),
                ),
                (
                    'morphospecies',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taxonomy.morphospecies'),
                ),
            ],
            options={
                'app_label': 'taxonomy',
                'unique_together': {('morphospecies', 'functional_group')},
            },
        ),
        migrations.RunPython(migrate_m2m_to_through, reverse_migrate_through_to_m2m),
        migrations.RemoveField(
            model_name='morphospecies',
            name='functional_groups',
        ),
        migrations.AddField(
            model_name='morphospecies',
            name='functional_groups',
            field=models.ManyToManyField(
                blank=True,
                through='taxonomy.MorphospeciesFunctionalGroup',
                to='taxonomy.functionalgroup',
            ),
        ),
    ]
