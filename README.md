# Ecommerce API

API REST completa para sistema de ecommerce desarrollada con Django REST Framework.

## Características principales

- Autenticación por tokens con roles diferenciados
- Sistema de permisos granular (Administrador/Visitante)
- Catálogo de productos con filtrado y búsqueda
- Gestión de categorías y proveedores
- Sistema de órdenes/pedidos con permisos por propietario
- Datos geográficos para direcciones
- Documentación automática con Swagger/OpenAPI

## Instalación rápida con Docker

### Requisitos previos
- Docker
- Docker Compose

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd ecommerce
```

### 2. Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:
```env
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=postgres123
```

### 3. Levantar el proyecto
```bash
docker-compose up -d
```

### 4. Crear usuarios de prueba
```bash
docker-compose exec web python manage.py init_groups
docker-compose exec web python manage.py create_test_users
```

La API estará disponible en: http://localhost:8000

## Documentación de la API

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/

## Usuarios de prueba

Después de ejecutar el comando de creación de usuarios tendrás:

**Administrador:**
- Username: `admin_test`
- Password: `admin123`
- Permisos: Acceso completo

**Visitante:**
- Username: `visitante_test`
- Password: `visitante123`
- Permisos: Solo lectura + gestión de sus propias órdenes

## Roles y permisos

### Público (sin autenticación)
- Ver catálogo básico de productos
- Ver categorías
- Consultar ubicaciones geográficas

### Visitante (usuario registrado)
- Todo lo público más:
- Ver catálogo completo de productos
- Ver proveedores
- Crear y ver sus propias órdenes
- Ver su perfil

### Administrador
- Todo lo del visitante más:
- Gestión completa de productos, categorías y proveedores
- Ver todas las órdenes del sistema
- Eliminar órdenes

## Endpoints principales

### Autenticación
- `POST /api/register/` - Registrar usuario
- `POST /api/login/` - Iniciar sesión
- `GET /api/profile/` - Ver perfil

### Productos
- `GET /api/product/` - Listar productos (autenticado)
- `GET /api/product/public_catalog/` - Catálogo público
- `POST /api/product/` - Crear producto (admin)

### Categorías
- `GET /api/category/` - Listar categorías (autenticado)
- `GET /api/category/public_list/` - Lista pública
- `POST /api/category/` - Crear categoría (admin)

### Órdenes
- `GET /api/order/` - Listar órdenes
- `POST /api/order/` - Crear orden
- `GET /api/order/my_orders/` - Mis órdenes

## Ejemplos de uso

### 1. Obtener token de autenticación
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_test", "password": "admin123"}'
```

### 2. Listar productos con autenticación
```bash
curl -H "Authorization: Token tu_token_aqui" \
  http://localhost:8000/api/product/
```

### 3. Ver catálogo público
```bash
curl http://localhost:8000/api/product/public_catalog/
```

## Comandos útiles

### Para desarrollo
```bash
# Ver logs
docker-compose logs -f

# Acceder al contenedor
docker-compose exec web bash

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Parar el proyecto
docker-compose down
```

### Reset de datos de prueba
```bash
# Reset usuarios
docker-compose exec web python manage.py create_test_users --reset

# Reset grupos y permisos
docker-compose exec web python manage.py init_groups --reset
```

## Estructura del proyecto

```
ecommerce/
├── apps/
│   ├── category/          # Gestión de categorías
│   ├── geo/              # Países, provincias, ciudades
│   ├── order/            # Sistema de órdenes
│   ├── person/           # Usuarios y autenticación
│   ├── product/          # Catálogo de productos
│   ├── suppliers/        # Gestión de proveedores
│   └── utils/            # Permisos y utilidades
├── ecommerce/            # Configuración Django
├── docker-compose.yml    # Configuración Docker
├── Dockerfile           # Imagen de la aplicación
└── requirements.txt     # Dependencias Python
```

## Solución de problemas

### La aplicación no inicia
- Verificar que Docker esté ejecutándose
- Comprobar que el archivo `.env` existe y tiene los valores correctos
- Revisar logs: `docker-compose logs`

### Error de conexión a la base de datos
- Esperar unos segundos para que PostgreSQL termine de inicializar
- Verificar que las variables del `.env` coincidan en todos los servicios

### Problemas de permisos
- Verificar que el token esté en el header: `Authorization: Token tu_token`
- Confirmar el rol del usuario con el comando de usuarios de prueba

### Token inválido
- El token puede haber expirado
- Hacer login nuevamente: `POST /api/login/`

## Desarrollo

Para desarrollo local sin Docker:

1. Crear entorno virtual: `python -m venv venv`
2. Activar entorno: `source venv/bin/activate`
3. Instalar dependencias: `pip install -r requirements.txt`
4. Configurar base de datos PostgreSQL
5. Ejecutar migraciones: `python manage.py migrate`
6. Crear usuarios: `python manage.py create_test_users`
7. Ejecutar servidor: `python manage.py runserver`

## Licencia

Este proyecto está bajo la Licencia MIT.