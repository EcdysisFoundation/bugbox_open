from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taxonomy', '0016_functionalgroup_and_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='morphospecies',
            name='taxonomy_identified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='morphospecies',
            name='taxonomy_reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='morphospecies',
            name='taxonomy_reviewed_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='morphospecies_taxonomy_reviews',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='morphospecies',
            name='taxonomy_unable_to_identify',
            field=models.BooleanField(default=False),
        ),
    ]
