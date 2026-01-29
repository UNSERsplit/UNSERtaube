#!/bin/sh

cd /app
echo receiving certificate
./renew_cert.sh
echo starting nginx
nginx
echo starting backend
cd /app/backend

export EXTERNAL_IP=$(ip -br a | grep "UP" | grep -vi "br-" | sed -r "s/.* *UP *(.*) /\1/g" | cut -d " " -f 1 | grep -v ":")

exec fastapi run main.py --host 127.0.0.1 --port 8000 --forwarded-allow-ips="127.0.0.1" --root-path /api