FROM python:3.12

RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# แยก requirements ก่อน เพื่อใช้ cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# แยก package.json ก่อน เพื่อใช้ cache
COPY theme/static_src/package*.json ./theme/static_src/
WORKDIR /app/theme/static_src
RUN npm install

# ค่อย copy source code ที่เหลือ
WORKDIR /app
COPY . .

CMD ["sh", "-c", "python manage.py migrate && python create_user.py && python manage.py runserver 0.0.0.0:8000"]