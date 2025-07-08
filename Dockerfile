FROM python:3.12

RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

WORKDIR /app/theme/static_src
RUN npm install

WORKDIR /app

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]