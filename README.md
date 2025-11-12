# E-commerce API con Django y Docker

Este proyecto es una API RESTful para una plataforma de E-commerce, desarrollada con Django y Django REST Framework. Toda la aplicación está containerizada utilizando Docker y Docker Compose para un despliegue y desarrollo simplificado y consistente.

## Tabla de Contenidos
1.  [Características Principales](#características-principales)
2.  [Tecnologías Utilizadas](#tecnologías-utilizadas)
3.  [Estructura del Proyecto](#estructura-del-proyecto)
4.  [Requisitos Previos](#requisitos-previos)
5.  [Instalación y Ejecución](#instalación-y-ejecución)
6.  [Acceso a la API](#acceso-a-la-api)
7.  [Funcionamiento del Arranque con Docker](#funcionamiento-del-arranque-con-docker)

---

## Características Principales

- **API RESTful**: Construida siguiendo los principios de REST para una comunicación cliente-servidor clara y predecible.
- **Containerización Completa**: Usa Docker para encapsular la aplicación y la base de datos, garantizando que funcione de la misma manera en cualquier entorno.
- **Base de Datos PostgreSQL**: Utiliza PostgreSQL, una base de datos relacional potente y robusta.
- **Documentación Automática de API**: Integrado con `drf-spectacular` para generar un esquema OpenAPI (Swagger UI) de forma automática.
- **Arranque Robusto**: Incluye un mecanismo de espera que asegura que la aplicación no intente conectarse a la base de datos hasta que esta esté completamente lista, evitando errores de conexión al inicio.
- **Migraciones Automáticas**: Las migraciones de la base de datos de Django se aplican automáticamente cada vez que se inician los contenedores.

## Tecnologías Utilizadas

- **Backend**: Django, Django REST Framework
- **Base de Datos**: PostgreSQL
- **Containerización**: Docker, Docker Compose
- **Documentación de API**: `drf-spectacular` (para OpenAPI/Swagger)
- **Driver de Base de Datos**: `psycopg2-binary`
- **Gestión de Entorno**: `python-dotenv`

## Estructura del Proyecto

```
ecommerce/
├── apps/                   # Directorio para las aplicaciones de Django
│   ├── person/
│   └── ...
├── ecommerce/              # Directorio de configuración del proyecto Django
│   ├── settings.py         # Configuración principal
│   └── urls.py             # URLs principales
├── .env.example            # Archivo de ejemplo para las variables de entorno
├── docker-compose.yml      # Orquesta los servicios de la aplicación (web y db)
├── Dockerfile              # Define cómo construir la imagen Docker para la app web
├── entrypoint.sh           # Script que se ejecuta al iniciar el contenedor web
├── manage.py               # Utilidad de línea de comandos de Django
├── requirements.txt        # Dependencias de Python
└── wait-for-postgres.sh    # Script de utilidad para esperar a que la BD esté lista
```

## Requisitos Previos

Asegúrate de tener instaladas las siguientes herramientas en tu sistema:

- Docker
- Docker Compose (generalmente incluido con Docker Desktop)

## Instalación y Ejecución

Sigue estos pasos para clonar, configurar y ejecutar el proyecto en tu máquina local.

**1. Clona el Repositorio**

```bash
git clone <URL_DEL_REPOSITORIO>
cd ecommerce
```

**2. Crea el archivo de variables de entorno**

Este proyecto utiliza un archivo `.env` para gestionar las credenciales de la base de datos y otras configuraciones. Puedes copiar el archivo de ejemplo:

```bash
cp .env.example .env
```

El contenido del archivo `.env` debería ser el siguiente. Puedes cambiar los valores si lo deseas, pero los valores por defecto funcionarán sin problemas.

```env
# .env
DB_NAME=ecommerceDjango
DB_USER=user
DB_PASSWORD=password
```

**3. Construye y Levanta los Contenedores**

Este es el comando principal. Construirá la imagen de Docker para el servicio `web` (si no existe o si se han hecho cambios en el `Dockerfile`) y luego iniciará todos los servicios.

```bash
docker compose up --build
```

La primera vez que ejecutes este comando, Docker descargará la imagen de `postgres` y la de `python`, instalará las dependencias y configurará todo. Los logs en tu terminal mostrarán el proceso de arranque, incluyendo la espera de la base de datos y la ejecución de las migraciones.

Para detener los contenedores, presiona `Ctrl + C` en la terminal donde se están ejecutando, y luego ejecuta:

```bash
docker compose down
```

## Acceso a la API

- **API Principal**: Una vez que los contenedores estén en funcionamiento, la API estará disponible en `http://localhost:8000/`.
- **Documentación de la API (Swagger UI)**: Puedes acceder a la documentación interactiva generada por drf-spectacular en `http://localhost:8000/api/schema/swagger-ui/`.
- **Conexión a la Base de Datos**: El servicio de PostgreSQL está expuesto en el puerto `5433` de tu máquina local y se conecta al puerto `5432` del contenedor. Puedes usar un cliente de base de datos como DBeaver o pgAdmin para conectarte usando las credenciales del archivo `.env`.

## Funcionamiento del Arranque con Docker

El proceso de arranque está diseñado para ser robusto y evitar errores comunes de conexión:

1.  **`docker compose up`**: Docker Compose lee el `docker-compose.yml` e inicia los servicios `db` y `web`.
2.  **Servicio `db`**: El contenedor de PostgreSQL se inicia. Si es la primera vez, crea la base de datos y el usuario especificados en el archivo `.env`.
3.  **Servicio `web`**:
    -   El `Dockerfile` define que el `ENTRYPOINT` del contenedor es el script `/entrypoint.sh`.
    -   `entrypoint.sh` se ejecuta y su primera tarea es llamar a `wait-for-postgres.sh`.
    -   `wait-for-postgres.sh` entra en un bucle, intentando conectarse al host `db` en el puerto `5432` cada segundo. No continuará hasta que la conexión sea exitosa.
    -   Una vez que la base de datos está lista, `entrypoint.sh` ejecuta el comando `python manage.py migrate` para aplicar las migraciones.
    -   Finalmente, `entrypoint.sh` ejecuta el comando `CMD` del `Dockerfile`, que es `python manage.py runserver 0.0.0.0:8000`, iniciando el servidor de Django.

Este flujo garantiza que la aplicación solo se inicie después de que la base de datos esté completamente inicializada y las migraciones se hayan aplicado.
