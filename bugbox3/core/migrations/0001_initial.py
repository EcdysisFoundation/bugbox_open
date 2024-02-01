from django.db import migrations

from django.contrib.postgres.operations import HStoreExtension, BtreeGinExtension, CreateExtension

class Migration(migrations.Migration):

    dependencies = []

    operations = [HStoreExtension(), BtreeGinExtension(), CreateExtension("postgis")]