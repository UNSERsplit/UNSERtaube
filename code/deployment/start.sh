#!/bin/sh

cd /app

./renew_cert.sh

nginx

cd /app/backend
exec fastapi run main.py --host 127.0.0.1 --port 8000 --forwarded-allow-ips="127.0.0.1" --root-path /api