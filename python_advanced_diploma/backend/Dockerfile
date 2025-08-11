FROM python:3.10-slim

# 1. Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
    curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Настройка рабочей директории
WORKDIR /app

# 3. Копирование только файлов зависимостей
COPY pyproject.toml poetry.lock* ./

# 4. Проверка содержимого рабочей директории
RUN ls -la && \
    [ -f pyproject.toml ] || (echo "ERROR: pyproject.toml not found!" && exit 1)

# 5. Установка Poetry (явно указываем версию)
RUN pip install --no-cache-dir "poetry==1.7.0" && \
    poetry config virtualenvs.create false && \
    poetry config experimental.new-installer false

# 6. Установка зависимостей с обработкой ошибок
RUN echo "Current Python version:" && python --version && \
    echo "Current Poetry version:" && poetry --version && \
    poetry install --no-interaction --no-ansi --no-root || \
    (echo "FAILED: poetry install exited with $?. Trying alternative approach..." && \
     pip install --no-cache-dir -r <(poetry export --without-hashes --format=requirements.txt))

# 7. Копирование остального кода
COPY . .

# 8. Установка пакета
RUN poetry install --no-interaction --no-ansi || \
    pip install --no-cache-dir .

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]