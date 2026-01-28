# 🛍️ Ecommerce API

API REST completa para sistema de ecommerce desarrollada con Django REST Framework.

## 📋 Características

- **Autenticación por tokens** con roles diferenciados
- **Sistema de permisos** granular (Administrador/Visitante)
- **Catálogo de productos** con filtrado y búsqueda
- **Gestión de categorías** y proveedores
- **Sistema de órdenes/pedidos** con permisos por propietario
- **Datos geográficos** para direcciones
- **Documentación automática** con Swagger/OpenAPI

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd ecommerce
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
Crear archivo `.env` en la raíz del proyecto:
```env
DB_NAME=tu_db_name
DB_USER=tu_db_user
DB_PASSWORD=tu_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Ejecutar migraciones
```bash
python manage.py migrate
```

### 6. Crear grupos y usuarios de prueba
```bash
python manage.py init_groups
python manage.py create_test_users
```

### 7. Ejecutar servidor
```bash
python manage.py runserver
```

## 📚 Documentación de la API

### 🌐 Acceso a Swagger UI
- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/
- **Schema JSON**: http://127.0.0.1:8000/api/schema/

## 👥 Roles y Permisos

### 🔑 Sistema de Autenticación
La API utiliza **Token Authentication**. Para acceder a endpoints protegidos:

1. Obtén un token: `POST /api/login/`
2. Incluye el token en el header: `Authorization: Token tu_token_aqui`

### 👤 Roles de Usuario

#### **🌐 Público** (sin autenticación)
- ✅ Ver catálogo de productos básico
- ✅ Ver lista de categorías
- ✅ Consultar ubicaciones geográficas

#### **👋 Visitante** (usuario registrado)
- ✅ Todo lo público +
- ✅ Ver catálogo completo de productos
- ✅ Ver detalles de productos
- ✅ Ver proveedores
- ✅ Crear sus propias órdenes
- ✅ Ver solo sus órdenes
- ✅ Ver su perfil
- ❌ Modificar productos, categorías o proveedores

#### **⚡ Administrador** (usuario admin)
- ✅ Todo lo del visitante +
- ✅ Crear/editar/eliminar productos
- ✅ Crear/editar/eliminar categorías
- ✅ Crear/editar/eliminar proveedores
- ✅ Ver todas las órdenes del sistema
- ✅ Eliminar órdenes

## 📊 Endpoints Principales

### 🔐 Autenticación
| Endpoint | Método | Descripción | Acceso |
|----------|--------|-------------|--------|
| `/api/register/` | POST | Registrar nuevo usuario | Público |
| `/api/login/` | POST | Iniciar sesión | Público |
| `/api/profile/` | GET | Ver perfil de usuario | Autenticado |

### 🛍️ Productos
| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/api/product/` | GET, POST | Listar/Crear productos | GET: Visitante+, POST: Admin |
| `/api/product/{id}/` | GET, PUT, DELETE | Ver/Editar/Eliminar | GET: Visitante+, PUT/DELETE: Admin |
| `/api/product/public_catalog/` | GET | Catálogo público básico | Público |

### 📂 Categorías
| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/api/category/` | GET, POST | Listar/Crear categorías | GET: Visitante+, POST: Admin |
| `/api/category/{id}/` | GET, PUT, DELETE | Ver/Editar/Eliminar | GET: Visitante+, PUT/DELETE: Admin |
| `/api/category/public_list/` | GET | Lista pública | Público |

### 🏢 Proveedores
| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/api/suppliers/` | GET, POST | Listar/Crear proveedores | GET: Visitante+, POST: Admin |
| `/api/suppliers/{id}/` | GET, PUT, DELETE | Ver/Editar/Eliminar | GET: Visitante+, PUT/DELETE: Admin |

### 📋 Órdenes
| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/api/order/` | GET, POST | Listar/Crear órdenes | Admin: todas, Visitante: propias |
| `/api/order/{id}/` | GET, PUT, DELETE | Ver/Editar/Eliminar | Propietario o Admin |
| `/api/order/my_orders/` | GET | Mis órdenes | Visitante+ |

### 🌍 Geografía
| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/api/geo/countries/` | GET | Lista de países | Público |
| `/api/geo/provinces/?country_id=1` | GET | Provincias por país | Público |
| `/api/geo/cities/?province_id=1` | GET | Ciudades por provincia | Público |

## 🧪 Usuarios de Prueba

El comando `python manage.py create_test_users` crea estos usuarios:

### 👑 Administrador
- **Username**: `admin_test`
- **Password**: `admin123`
- **Rol**: Administrador
- **Permisos**: Acceso completo

### 👤 Visitante
- **Username**: `visitante_test`
- **Password**: `visitante123`
- **Rol**: Visitante
- **Permisos**: Solo lectura + gestión de propias órdenes

### 👥 Usuario Normal
- **Username**: `user_normal`
- **Password**: `user123`
- **Rol**: Visitante
- **Permisos**: Solo lectura + gestión de propias órdenes

## 🔧 Ejemplos de Uso

### 1. Obtener Token de Autenticación
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_test",
    "password": "admin123"
  }'
```

**Respuesta:**
```json
{
  "token": "9340ff6d6806e7dc37d7...",
  "user_id": 1,
  "username": "admin_test",
  "message": "Login successful"
}
```

### 2. Listar Productos (con autenticación)
```bash
curl -H "Authorization: Token 9340ff6d6806e7dc37d7..." \
  http://127.0.0.1:8000/api/product/
```

### 3. Ver Catálogo Público (sin autenticación)
```bash
curl http://127.0.0.1:8000/api/product/public_catalog/
```

### 4. Crear Producto (solo admin)
```bash
curl -X POST http://127.0.0.1:8000/api/product/ \
  -H "Authorization: Token tu_token_admin" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Producto Test",
    "stock": 10,
    "color": 1,
    "size": 1
  }'
```

### 5. Crear Orden (visitante)
```bash
curl -X POST http://127.0.0.1:8000/api/order/ \
  -H "Authorization: Token tu_token_visitante" \
  -H "Content-Type: application/json" \
  -d '{
    "total": 199.99
  }'
```

## 🔍 Filtrado y Búsqueda

### Productos
```bash
# Buscar por nombre
GET /api/product/?search=camiseta

# Filtrar por categoría
GET /api/product/?categories=1

# Ordenar por stock
GET /api/product/?ordering=stock

# Combinado
GET /api/product/?search=deportiva&categories=2&ordering=name
```

### Categorías
```bash
# Buscar por nombre o descripción
GET /api/category/?search=ropa

# Ordenar alfabéticamente
GET /api/category/?ordering=name
```

## 🏗️ Arquitectura del Proyecto

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
├── ecommerce/            # Configuración principal
├── logs/                 # Archivos de log (ignorados por git)
└── requirements.txt      # Dependencias
```

## 🛠️ Comandos Útiles

```bash
# Crear grupos y permisos
python manage.py init_groups

# Crear usuarios de prueba
python manage.py create_test_users

# Reset usuarios de prueba
python manage.py create_test_users --reset

# Reset grupos y permisos
python manage.py init_groups --reset

# Generar schema de API
python manage.py spectacular --color --file schema.yml

# Ver logs en tiempo real (si están configurados)
tail -f logs/ecommerce.log
```

## 🐛 Solución de Problemas

### Error: "Unable to log in with provided credentials"
- Verifica username y password
- Asegúrate de que el usuario existe: `python manage.py create_test_users`

### Error: Permission denied
- Verifica que el token esté en el header: `Authorization: Token tu_token`
- Confirma que el usuario tenga los permisos necesarios
- Los administradores pueden acceder a todo
- Los visitantes solo a endpoints de lectura y sus propias órdenes

### Error: Token inválido
- El token puede haber expirado o ser incorrecto
- Haz login nuevamente: `POST /api/login/`

## 🚀 Próximas Funcionalidades

- [ ] Dashboard de administración con estadísticas
- [ ] Sistema de inventario avanzado
- [ ] Notificaciones por email
- [ ] Carrito de compras persistente
- [ ] Sistema de pagos
- [ ] API de envíos
- [ ] Sistema de reviews y calificaciones

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o soporte, contacta al equipo de desarrollo.