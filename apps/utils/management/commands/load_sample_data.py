import random

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from apps.category.models import Category
from apps.color.models import Color
from apps.geo.models import City, Country, Province
from apps.person.models import Person
from apps.product.models import Product
from apps.size.models import Size
from apps.suppliers.models import Suppliers


class Command(BaseCommand):
    help = "Carga datos de ejemplo para testing del sistema"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Limpiar datos existentes antes de cargar",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Limpiando datos existentes...")
            self.clear_data()

        self.stdout.write("Cargando datos de ejemplo...")

        # Crear grupos de usuario
        self.create_user_groups()

        # Crear usuarios
        self.create_users()

        # Crear datos geográficos básicos
        self.create_geo_data()

        # Crear colores y tamaños
        self.create_colors_and_sizes()

        # Crear categorías
        self.create_categories()

        # Crear proveedores
        self.create_suppliers()

        # Crear productos
        self.create_products()

        self.stdout.write(
            self.style.SUCCESS("✅ Datos de ejemplo cargados exitosamente!")
        )

        # Mostrar resumen
        self.show_summary()

    def clear_data(self):
        """Limpia datos de ejemplo existentes"""
        Product.objects.all().delete()
        Category.objects.all().delete()
        Suppliers.objects.all().delete()
        Color.objects.all().delete()
        Size.objects.all().delete()
        Person.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("✅ Datos limpiados")

    def create_user_groups(self):
        """Crea grupos de usuario"""
        admin_group, created = Group.objects.get_or_create(name="Administrador")
        visitor_group, created = Group.objects.get_or_create(name="Visitante")

        if created:
            self.stdout.write("✅ Grupos de usuario creados")
        else:
            self.stdout.write("⚪ Grupos de usuario ya existían")

    def create_users(self):
        """Crea usuarios de ejemplo"""
        # Usuario administrador
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_user(
                username="admin",
                password="admin123",
                email="admin@ecommerce.com",
                first_name="Administrator",
                last_name="System",
            )
            admin.groups.add(Group.objects.get(name="Administrador"))
            self.stdout.write("✅ Usuario administrador creado (admin/admin123)")

        # Usuario visitante
        if not User.objects.filter(username="visitor").exists():
            visitor = User.objects.create_user(
                username="visitor",
                password="visitor123",
                email="visitor@ecommerce.com",
                first_name="Visitor",
                last_name="User",
            )
            visitor.groups.add(Group.objects.get(name="Visitante"))

            # Crear perfil de persona para el visitante
            Person.objects.create(
                user=visitor,
                name="Juan",
                last_name="Pérez",
                dni="12345678",
                city_id=1,  # Asumiendo que existe ciudad con ID 1
            )
            self.stdout.write("✅ Usuario visitante creado (visitor/visitor123)")

    def create_geo_data(self):
        """Crea datos geográficos básicos si no existen"""
        if not Country.objects.exists():
            country = Country.objects.create(name="Argentina")
            province = Province.objects.create(name="Buenos Aires", country=country)
            City.objects.create(name="CABA", province=province)
            self.stdout.write("✅ Datos geográficos básicos creados")

    def create_colors_and_sizes(self):
        """Crea colores y tamaños básicos"""
        colors_data = [
            "Rojo",
            "Azul",
            "Verde",
            "Negro",
            "Blanco",
            "Amarillo",
            "Rosa",
            "Violeta",
            "Naranja",
            "Gris",
        ]

        for color_name in colors_data:
            Color.objects.get_or_create(title=color_name)

        sizes_data = ["XS", "S", "M", "L", "XL", "XXL"]

        for size_name in sizes_data:
            Size.objects.get_or_create(title=size_name)

        self.stdout.write("✅ Colores y tamaños creados")

    def create_categories(self):
        """Crea categorías de ejemplo"""
        categories_data = [
            "Ropa",
            "Calzado",
            "Accesorios",
            "Deportes",
            "Electrónicos",
            "Hogar",
            "Libros",
            "Belleza",
            "Juguetes",
            "Música",
        ]

        for category_name in categories_data:
            Category.objects.get_or_create(name=category_name)

        self.stdout.write("✅ Categorías creadas")

    def create_suppliers(self):
        """Crea proveedores de ejemplo"""
        suppliers_data = [
            "Proveedor Premium SA",
            "Distribuidora Central",
            "Importaciones Global",
            "Textiles del Sur",
            "Electrónicos Norte",
            "Calzados Modernos",
            "Accesorios Fashion",
            "Deportes Total",
            "Casa y Hogar",
            "Libros Universales",
        ]

        for supplier_name in suppliers_data:
            Suppliers.objects.get_or_create(
                company_name=supplier_name,
                defaults={
                    "contact_person": "Contacto " + supplier_name.split()[0],
                    "contact_email": f"contacto@{supplier_name.lower().replace(' ', '')}.com",
                    "adress": f"Dirección {supplier_name}",
                    "city_id": 1,
                },
            )

        self.stdout.write("✅ Proveedores creados")

    def create_products(self):
        """Crea productos de ejemplo"""
        categories = list(Category.objects.all())
        suppliers = list(Suppliers.objects.all())
        colors = list(Color.objects.all())
        sizes = list(Size.objects.all())

        products_data = [
            # Ropa
            (
                "Camiseta Básica",
                25,
                50,
                "https://via.placeholder.com/300x300/FF0000/FFFFFF?text=Camiseta",
            ),
            (
                "Pantalón Jeans",
                15,
                75,
                "https://via.placeholder.com/300x300/0000FF/FFFFFF?text=Jeans",
            ),
            (
                "Vestido Casual",
                12,
                85,
                "https://via.placeholder.com/300x300/FF69B4/FFFFFF?text=Vestido",
            ),
            (
                "Sweater Invierno",
                8,
                95,
                "https://via.placeholder.com/300x300/008000/FFFFFF?text=Sweater",
            ),
            (
                "Camisa Formal",
                20,
                65,
                "https://via.placeholder.com/300x300/000000/FFFFFF?text=Camisa",
            ),
            # Calzado
            (
                "Zapatillas Running",
                30,
                120,
                "https://via.placeholder.com/300x300/FF8C00/FFFFFF?text=Zapatillas",
            ),
            (
                "Botas de Cuero",
                18,
                150,
                "https://via.placeholder.com/300x300/8B4513/FFFFFF?text=Botas",
            ),
            (
                "Sandalias Verano",
                25,
                45,
                "https://via.placeholder.com/300x300/FFD700/FFFFFF?text=Sandalias",
            ),
            # Accesorios
            (
                "Gorro de Lana",
                40,
                25,
                "https://via.placeholder.com/300x300/800080/FFFFFF?text=Gorro",
            ),
            (
                "Cinturón de Cuero",
                15,
                35,
                "https://via.placeholder.com/300x300/654321/FFFFFF?text=Cinturon",
            ),
            (
                "Bolso de Mano",
                22,
                80,
                "https://via.placeholder.com/300x300/DC143C/FFFFFF?text=Bolso",
            ),
            # Deportes
            (
                "Pelota de Fútbol",
                35,
                40,
                "https://via.placeholder.com/300x300/000000/FFFFFF?text=Pelota",
            ),
            (
                "Raqueta de Tenis",
                12,
                180,
                "https://via.placeholder.com/300x300/FFFF00/000000?text=Raqueta",
            ),
            (
                "Pesas 5kg",
                20,
                60,
                "https://via.placeholder.com/300x300/696969/FFFFFF?text=Pesas",
            ),
            # Electrónicos
            (
                "Auriculares Bluetooth",
                45,
                90,
                "https://via.placeholder.com/300x300/1E90FF/FFFFFF?text=Auriculares",
            ),
            (
                "Cargador USB-C",
                60,
                25,
                "https://via.placeholder.com/300x300/32CD32/FFFFFF?text=Cargador",
            ),
            # Con stock bajo para testing
            (
                "Producto Stock Bajo",
                3,
                299,
                "https://via.placeholder.com/300x300/FF0000/FFFFFF?text=Stock+Bajo",
            ),
            (
                "Producto Agotado",
                0,
                199,
                "https://via.placeholder.com/300x300/808080/FFFFFF?text=Agotado",
            ),
        ]

        created_count = 0
        for name, stock, price_hint, img_url in products_data:
            if not Product.objects.filter(name=name).exists():
                # Seleccionar color y tamaño aleatorios
                color = random.choice(colors)
                size = random.choice(sizes)

                # Crear el producto
                product = Product.objects.create(
                    name=name,
                    stock=stock,
                    img=img_url,
                    color=color,
                    size=size,
                    is_active=True,
                )

                # Asignar categorías aleatorias (1-3 categorías por producto)
                num_categories = random.randint(1, min(3, len(categories)))
                selected_categories = random.sample(categories, num_categories)
                product.categories.set(selected_categories)

                # Asignar proveedores aleatorios (1-2 proveedores por producto)
                num_suppliers = random.randint(1, min(2, len(suppliers)))
                selected_suppliers = random.sample(suppliers, num_suppliers)
                product.suppliers.set(selected_suppliers)

                created_count += 1

        self.stdout.write(f"✅ {created_count} productos creados")

    def show_summary(self):
        """Muestra resumen de datos cargados"""
        self.stdout.write(self.style.SUCCESS("\n📊 RESUMEN DE DATOS CARGADOS:"))
        self.stdout.write(f"👥 Usuarios: {User.objects.count()}")
        self.stdout.write(f"👤 Personas: {Person.objects.count()}")
        self.stdout.write(f"🎨 Colores: {Color.objects.count()}")
        self.stdout.write(f"📏 Tamaños: {Size.objects.count()}")
        self.stdout.write(f"📂 Categorías: {Category.objects.count()}")
        self.stdout.write(f"🏭 Proveedores: {Suppliers.objects.count()}")
        self.stdout.write(f"📦 Productos: {Product.objects.count()}")
        self.stdout.write(
            f"   ├─ Disponibles: {Product.get_available_products().count()}"
        )
        self.stdout.write(
            f"   ├─ Stock bajo: {Product.get_low_stock_products().count()}"
        )
        self.stdout.write(
            f"   └─ Sin stock: {Product.get_out_of_stock_products().count()}"
        )

        self.stdout.write(self.style.SUCCESS("\n🔗 USUARIOS DE PRUEBA:"))
        self.stdout.write("👨‍💼 Admin: admin / admin123")
        self.stdout.write("👤 Visitante: visitor / visitor123")

        self.stdout.write(self.style.SUCCESS("\n🚀 ENDPOINTS PARA PROBAR:"))
        self.stdout.write("📋 Lista productos: GET /api/product/")
        self.stdout.write("🔍 Detalle producto: GET /api/product/{id}/")
        self.stdout.write("🌐 Catálogo público: GET /api/product/public_catalog/")
        self.stdout.write("📉 Stock bajo: GET /api/product/low_stock/")
        self.stdout.write("🚫 Sin stock: GET /api/product/out_of_stock/")
        self.stdout.write("📖 Documentación: GET /api/docs/")
