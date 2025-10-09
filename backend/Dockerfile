
# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala poetry
RUN pip install poetry

# Copia los archivos de configuración de Poetry
COPY poetry.lock pyproject.toml ./

# Configura Poetry para no crear un entorno virtual y luego instala las dependencias
RUN poetry config virtualenvs.create false \
  && poetry install --no-root --only main --no-interaction --no-ansi

# Instalar navegadores de Playwright
RUN playwright install chromium

# Instalar dependencias del sistema para Playwright
RUN playwright install-deps

# Copia el código de la aplicación
COPY ./app /app/app
