# Usa una imagen de Python como base
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido actual del directorio de trabajo al contenedor en /app
COPY . /app

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3018
# Indica que el punto de entrada de la aplicación es __main__.py
CMD ["python", "__main__.py"]
