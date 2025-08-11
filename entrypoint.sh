#!/bin/sh

# Aplica migraciones
python manage.py migrate

# (Opcional) crear migraciones si hiciste cambios en modelos:
# python manage.py makemigrations

# Arranca el servidor
python manage.py runserver 0.0.0.0:8000

#ejecuta este comando para darle permisos  localmente:
##chmod +x entrypoint.sh
