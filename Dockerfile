# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia requirements.txt (o requirements base) primero para aprovechar el cache
COPY requirements.txt .

# Instala las dependencias
RUN apt-get update && apt-get install -y netcat-traditional && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean

# Copia el resto del código de la app
COPY . .

#Copia script de arranque personalizado
COPY entrypoint.sh /entrypoint.sh
COPY wait-for-postgres.sh /wait-for-postgres.sh

#Da permisos de ejecución al script
RUN chmod +x /entrypoint.sh && chmod +x /wait-for-postgres.sh

# Expone el puerto que usa Django (por defecto 8000)
EXPOSE 8000

# El ENTRYPOINT se ejecuta siempre al iniciar el contenedor.
ENTRYPOINT ["/entrypoint.sh"]
# El CMD se pasa como argumento al ENTRYPOINT.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
