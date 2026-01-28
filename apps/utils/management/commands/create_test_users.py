# apps/utils/management/commands/create_test_users.py
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from apps.geo.models import City
from apps.person.models import Person


class Command(BaseCommand):
    help = "Crea usuarios de prueba con diferentes roles para testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina usuarios de prueba existentes antes de crearlos",
        )

    def handle(self, *args, **options):
        # Usuarios de prueba a crear
        test_users = [
            {
                "username": "admin_test",
                "email": "admin@test.com",
                "password": "admin123",
                "group": "Administrador",
                "person_data": {
                    "name": "Admin",
                    "last_name": "Tester",
                    "dni": "12345678",
                },
            },
            {
                "username": "visitante_test",
                "email": "visitante@test.com",
                "password": "visitante123",
                "group": "Visitante",
                "person_data": {
                    "name": "Visitante",
                    "last_name": "Tester",
                    "dni": "87654321",
                },
            },
            {
                "username": "user_normal",
                "email": "user@test.com",
                "password": "user123",
                "group": "Visitante",
                "person_data": {
                    "name": "Usuario",
                    "last_name": "Normal",
                    "dni": "11223344",
                },
            },
        ]

        if options["reset"]:
            self.stdout.write(self.style.WARNING("🗑️  Eliminando usuarios de prueba..."))
            usernames = [user["username"] for user in test_users]
            deleted_count = User.objects.filter(username__in=usernames).delete()[0]
            if deleted_count > 0:
                self.stdout.write(f"   Eliminados {deleted_count} usuarios")

        # Verificar que existan los grupos
        try:
            admin_group = Group.objects.get(name="Administrador")
            visitante_group = Group.objects.get(name="Visitante")
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Los grupos no existen. Ejecuta primero: python manage.py init_groups"
                )
            )
            return

        # Obtener ciudad por defecto
        try:
            default_city = City.objects.first()
            if not default_city:
                self.stdout.write(
                    self.style.WARNING("⚠️  No hay ciudades en la DB, usando ID=1")
                )
                default_city_id = 1
            else:
                default_city_id = default_city.id
        except:
            default_city_id = 1

        self.stdout.write("\n👥 Creando usuarios de prueba...")

        created_users = []
        for user_data in test_users:
            # Verificar si el usuario ya existe
            if User.objects.filter(username=user_data["username"]).exists():
                self.stdout.write(f"   • {user_data['username']} ya existe")
                continue

            try:
                # Crear usuario
                user = User.objects.create_user(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password"],
                )

                # Asignar grupo
                group = Group.objects.get(name=user_data["group"])
                user.groups.add(group)

                # Crear perfil de persona
                Person.objects.create(
                    user=user,
                    name=user_data["person_data"]["name"],
                    last_name=user_data["person_data"]["last_name"],
                    dni=user_data["person_data"]["dni"],
                    city_id=default_city_id,
                )

                # Crear token de autenticación
                Token.objects.create(user=user)

                created_users.append(
                    {
                        "username": user.username,
                        "password": user_data["password"],
                        "group": user_data["group"],
                        "token": Token.objects.get(user=user).key,
                    }
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"   ✓ {user.username} creado como {user_data['group']}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"   ❌ Error creando {user_data['username']}: {e}"
                    )
                )

        # Mostrar resumen
        if created_users:
            self.stdout.write("\n🎉 ¡Usuarios de prueba creados exitosamente!")
            self.stdout.write("\n📋 Credenciales para testing:")
            self.stdout.write("=" * 50)

            for user in created_users:
                self.stdout.write(f"\n👤 {user['group'].upper()}:")
                self.stdout.write(f"   Username: {user['username']}")
                self.stdout.write(f"   Password: {user['password']}")
                self.stdout.write(f"   Token:    {user['token'][:20]}...")

            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("\n🧪 URLs para probar en Postman:")
            self.stdout.write("   Login: POST http://127.0.0.1:8000/api/login/")
            self.stdout.write("   Products: GET http://127.0.0.1:8000/api/product/")
            self.stdout.write(
                "\n💡 Recuerda usar 'Token <token>' en el header Authorization"
            )

        else:
            self.stdout.write("\n⚠️  No se crearon usuarios nuevos")
