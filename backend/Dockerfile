FROM python:3.10.13-slim

WORKDIR /backend
ENV PYTHONPATH=/backend \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_NO_CACHE_DIR=1

# Устанавливаем системные зависимости для psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

# Устанавливаем poetry и зависимости
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir poetry==2.1.4 && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root || \
    { echo "Fallback to pip install"; pip install -e .; }

COPY backend/src/ ./src/

EXPOSE 5000
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]