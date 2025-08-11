# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia requirements.txt (o requirements base) primero para aprovechar el cache
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la app
COPY . .

#Copia script de arranque personalizado
COPY entrypoint.sh /entrypoint.sh  

#Da permisos de ejecución al script
RUN chmod +x entrypoint.sh

# Expone el puerto que usa Django (por defecto 8000)
EXPOSE 8000

# Comando para ejecutar la app con el servidor de desarrollo (cámbialo si usas gunicorn o similar)
CMD ["/entrypoint.sh"]
