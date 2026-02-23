
from django.db import migrations, models

from taxonomy.constants import FUNCTIONAL_GROUP_DEFINITIONS


def populate_functional_groups(apps, schema_editor):
    FunctionalGroup = apps.get_model("taxonomy", "FunctionalGroup")
    for code, display_name, description, category in FUNCTIONAL_GROUP_DEFINITIONS:
        FunctionalGroup.objects.get_or_create(
            code=code,
            defaults={
                "display_name": display_name,
                "description": description,
                "category": category,
            },
        )


def reverse_populate(apps, schema_editor):
    FunctionalGroup = apps.get_model("taxonomy", "FunctionalGroup")
    FunctionalGroup.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("taxonomy", "0015_morphospecies_tags"),
    ]

    operations = [
        migrations.CreateModel(
            name="FunctionalGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64, unique=True)),
                ("display_name", models.CharField(max_length=128)),
                ("description", models.TextField(blank=True)),
                ("category", models.CharField(max_length=32)),
            ],
            options={
                "app_label": "taxonomy",
            },
        ),
        migrations.AddField(
            model_name="morphospecies",
            name="functional_groups",
            field=models.ManyToManyField(blank=True, to="taxonomy.functionalgroup"),
        ),
        migrations.RunPython(populate_functional_groups, reverse_populate),
    ]
