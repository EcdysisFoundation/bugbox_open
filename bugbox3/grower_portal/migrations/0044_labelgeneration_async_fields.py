
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grower_portal", "0043_csvimportlog_category_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="labelgeneration",
            name="status",
            field=models.CharField(
                choices=[
                    ("queued", "Queued"),
                    ("processing", "Processing"),
                    ("ready", "Ready"),
                    ("failed", "Failed"),
                ],
                default="queued",
                help_text="Generation status",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="labelgeneration",
            name="generation_params",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Internal parameters used for async generation",
            ),
        ),
        migrations.AddField(
            model_name="labelgeneration",
            name="error_message",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Error details if generation failed",
            ),
        ),
        migrations.AddField(
            model_name="labelgeneration",
            name="task_id",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Celery task id",
                max_length=64,
            ),
        ),
    ]

