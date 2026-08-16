# Usar imagen base oficial de Python 3.11
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y forzar el volcado de stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema necesarias para Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar los navegadores de Playwright (solo Chromium para este proyecto) y sus dependencias del OS
RUN playwright install --with-deps chromium

# Copiar el resto del código del proyecto
COPY . .

# Comando para iniciar el bot
CMD ["python", "main.py"]
