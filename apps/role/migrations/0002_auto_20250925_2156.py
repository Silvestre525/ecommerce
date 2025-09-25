from django.db import migrations
from django.contrib.auth.models import Group

def create_initial_groups(apps, schema_editor):
    Group.objects.get_or_create(name='Visitante')
    Group.objects.get_or_create(name='Administrador')

class Migration(migrations.Migration):

    dependencies = [
        ('role', '0001_create_groups_permissions'),  # Dependencia de la migración inicial de role
    ]

    operations = [
        migrations.RunPython(create_initial_groups),
    ]
