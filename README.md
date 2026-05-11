# Ecommerce API 

API REST robusta para un sistema de ecommerce de indumentaria, desarrollada con **Django REST Framework**. Diseñada para integrarse fácilmente con frontends modernos (React, Angular, Vue) gestionando el carrito localmente.

## Características principales

- **Arquitectura de Software Avanzada**: Implementación estricta del patrón **Service Layer** y **Custom Managers**. Las vistas actúan como controladores delgados ("Thin Views"), separando completamente la lógica de negocio y de base de datos, lo que garantiza alta cohesión y bajo acoplamiento.
- **Seguridad en Precios**: El backend calcula automáticamente los totales de las órdenes basándose en precios de base de datos (evita manipulación del cliente).
- **Gestión de Stock Atómica**: Control de inventario en tiempo real con validación previa a la venta, delegando la complejidad al `ProductService`.
- **Historial de Precios**: Registro del precio de compra en cada ítem de la orden (`DetailOrder`).
- **Autenticación Modular**: Tokens con roles diferenciados (Administrador/Visitante) manejados de forma centralizada por el `AuthService`.
- **Sistema Geográfico Escalable**: Soporte para direcciones con relaciones en cascada (Countries, Provinces y Cities) provistas por el `GeoService`.
- **Documentación Completa**: OpenAPI/Swagger y [Guía de Lógica de Negocio](./docs/api_guide.md).

## Instalación (Recomendada con Docker)

### 1. Clonar y Configurar
```bash
git clone <url-del-repo>
cd ecommerce
cp .env.example .env  # Asegúrate de configurar tus variables
```

### 2. Levantar el Entorno
```bash
docker compose up -d --build
```

### 3. Cargar Datos de Prueba (Recomendado)
Este comando configura grupos, usuarios, productos, precios, talles y proveedores en un solo paso:
```bash
docker compose exec web python manage.py load_sample_data --clear
```

La API estará disponible en: [http://localhost:8000](http://localhost:8000)

##  Documentación

- **Guía de Desarrollo y Frontend**: [docs/api_guide.md](./docs/api_guide.md) (Lógica de negocio y flujos).
- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)

## Usuarios de prueba (Cargados con `load_sample_data`)

| Rol | Username | Password | Permisos |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | Control total del catálogo y órdenes |
| **Visitante** | `visitor` | `visitor123` | Compra de productos y ver órdenes propias |

##  Estructura del Proyecto

```text
ecommerce/
├── apps/
│   ├── category/      # Organización de productos
│   ├── order/         # Lógica de pedidos y DetailOrder (Detalles)
│   ├── person/        # Perfiles de usuario y Auth
│   ├── product/       # Catálogo con Variantes (Talla/Color) y Stock
│   ├── suppliers/     # Gestión de proveedores
│   └── geo/           # Datos de ubicación
├── core/              # Configuración global de Django/ASGI/WSGI
├── docs/              # Manuales de integración y lógica
└── docker-compose.yml # Orquestación de contenedores (Web, DB, Redis)
```

## Comandos útiles

```bash
# Ver logs del servidor
docker compose logs -f web

# Acceder a la consola de Django
docker compose exec web python manage.py shell

# Reiniciar base de datos y datos de prueba
docker compose exec web python manage.py load_sample_data --clear
```
