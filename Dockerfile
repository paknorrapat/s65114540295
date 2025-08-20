# ===== Stage 1: Builder (Python + Node for Tailwind) =====
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=myproject.settings \
    TZ=Asia/Bangkok

# OS deps + Node20 + build deps (psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg build-essential gcc pkg-config libpq-dev tzdata \
 && mkdir -p /etc/apt/keyrings \
 && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
     | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
 && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" \
     > /etc/apt/sources.list.d/nodesource.list \
 && apt-get update && apt-get install -y --no-install-recommends nodejs \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (cache-friendly)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Node deps (package.json อยู่ที่ theme/static_src/)
COPY theme/static_src/package*.json /app/theme/static_src/
WORKDIR /app/theme/static_src
RUN npm install

# โค้ดทั้งหมด
WORKDIR /app
COPY . .

# Build Tailwind (สคริปต์อยู่ใน theme/static_src/package.json)
WORKDIR /app/theme/static_src
RUN npm run build

# collectstatic (ต้องมี STATIC_ROOT ใน settings.py)
WORKDIR /app
RUN python manage.py collectstatic --noinput


# ===== Stage 2: Runtime (เฉพาะ Python, ไม่มี Node) =====
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=myproject.settings \
    TZ=Asia/Bangkok

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 tzdata netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps runtime
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn

# โค้ด + staticfiles ที่ build แล้ว
COPY . .
COPY --from=builder /app/staticfiles /app/staticfiles

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]