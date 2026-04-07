from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("taxonomy", "0018_morphospecies_reviewed_verbose_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="morphospecies",
            old_name="taxonomy_unable_to_identify",
            new_name="taxonomy_reviewed",
        ),
    ]
