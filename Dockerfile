FROM python:3.10-slim

# Ставим Nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и ставим зависимости
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ .

# Настраиваем Nginx
RUN rm /etc/nginx/sites-enabled/default
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Копируем скрипт запуска и даем права
COPY docker/start.sh .
RUN chmod +x start.sh

EXPOSE 80

CMD ["./start.sh"]
