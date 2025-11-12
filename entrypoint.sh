#!/bin/sh

# Espera a que la base de datos esté lista antes de continuar.
ol# El script wait-for-postgres.sh esperará y luego ejecutará el comando que se le pase.
/wait-for-postgres.sh "$DB_HOST" "echo 'Aplicando migraciones de la base de datos...'"
/wait-for-postgres.sh "$DB_HOST" "python manage.py migrate"

# Ejecuta el comando pasado a este script.
# En el Dockerfile, será `python manage.py runserver...` por defecto.
# Esto permite que docker-compose también pueda pasar otros comandos si es necesario (ej. un shell).
exec "$@"
