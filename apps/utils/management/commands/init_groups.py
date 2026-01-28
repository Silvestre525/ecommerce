# apps/utils/management/commands/init_groups.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.category.models import Category
from apps.order.models import Order
from apps.person.models import Person
from apps.product.models import Product
from apps.suppliers.models import Suppliers


class Command(BaseCommand):
    help = "Inicializa grupos y permisos del sistema de ecommerce"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina grupos existentes antes de crearlos",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Eliminando grupos existentes..."))
            Group.objects.filter(name__in=["Administrador", "Visitante"]).delete()

        # Crear grupos
        admin_group, created = Group.objects.get_or_create(name="Administrador")
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Administrador" creado'))
        else:
            self.stdout.write('• Grupo "Administrador" ya existe')

        visitante_group, created = Group.objects.get_or_create(name="Visitante")
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Visitante" creado'))
        else:
            self.stdout.write('• Grupo "Visitante" ya existe')

        # Configurar permisos para Administrador (acceso total)
        self._setup_admin_permissions(admin_group)

        # Configurar permisos para Visitante (solo lectura)
        self._setup_visitante_permissions(visitante_group)

        self.stdout.write(
            self.style.SUCCESS("\n🎉 Grupos y permisos configurados correctamente!")
        )

    def _setup_admin_permissions(self, admin_group):
        """Configura permisos completos para administradores"""
        self.stdout.write("\n📋 Configurando permisos para Administrador...")

        # Modelos que pueden administrar
        models = [Product, Category, Person, Suppliers, Order]
        permissions_added = 0

        for model in models:
            content_type = ContentType.objects.get_for_model(model)

            # Permisos CRUD completos
            permissions = Permission.objects.filter(
                content_type=content_type,
                codename__in=[
                    f"add_{model._meta.model_name}",
                    f"change_{model._meta.model_name}",
                    f"delete_{model._meta.model_name}",
                    f"view_{model._meta.model_name}",
                ],
            )

            for permission in permissions:
                admin_group.permissions.add(permission)
                permissions_added += 1

        self.stdout.write(f"  ✓ {permissions_added} permisos asignados a Administrador")

    def _setup_visitante_permissions(self, visitante_group):
        """Configura permisos de solo lectura para visitantes"""
        self.stdout.write("\n👥 Configurando permisos para Visitante...")

        # Modelos que pueden ver (solo lectura)
        models = [Product, Category, Suppliers]
        permissions_added = 0

        for model in models:
            content_type = ContentType.objects.get_for_model(model)

            # Solo permisos de vista
            try:
                view_permission = Permission.objects.get(
                    content_type=content_type, codename=f"view_{model._meta.model_name}"
                )
                visitante_group.permissions.add(view_permission)
                permissions_added += 1
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Permiso view_{model._meta.model_name} no encontrado"
                    )
                )

        # Permisos especiales para visitantes (ver su propio perfil)
        try:
            person_view = Permission.objects.get(
                content_type=ContentType.objects.get_for_model(Person),
                codename="view_person",
            )
            visitante_group.permissions.add(person_view)
            permissions_added += 1
        except Permission.DoesNotExist:
            pass

        self.stdout.write(f"  ✓ {permissions_added} permisos asignados a Visitante")
