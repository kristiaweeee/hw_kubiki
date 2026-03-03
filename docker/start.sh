#!/bin/bash
# Запускаем Gunicorn, привязываем его к unix-сокету и отправляем в фон
gunicorn --bind unix:/tmp/app.sock app:app &

# Запускаем Nginx на переднем плане
nginx -g "daemon off;"
