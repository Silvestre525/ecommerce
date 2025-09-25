from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Visitante")
    Group.objects.get_or_create(name="Administrador")

def delete_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Visitante", "Administrador"]).delete()

class Migration(migrations.Migration):
    dependencies = [("person", "0001_initial")]
    operations = [migrations.RunPython(create_groups, delete_groups)]
