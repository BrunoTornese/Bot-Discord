
# Usa la imagen base de Python Alpine
FROM python:3.11.5-alpine

# Establece el directorio de trabajo en la carpeta /app
WORKDIR /app

# Copia el contenido del directorio actual en el contenedor en /app
COPY . /app

# Instala las dependencias del bot
RUN pip install -r requirements.txt

# Instala Opus y FFmpeg
RUN apk add --no-cache opus ffmpeg

# Comando para ejecutar el bot
CMD [ "python", "src/index.py" ]

