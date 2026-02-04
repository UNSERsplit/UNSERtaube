#!/bin/sh

cd /app

mkdir -p /credentials_linux
cp /credentials/taube_rsa /credentials_linux/taube_rsa
chmod 600 /credentials_linux/taube_rsa

echo receiving certificate
./renew_cert.sh
echo starting nginx
nginx
echo starting backend
cd /app/backend

EXTERNAL_IP1=$(ip -br a | grep "UP" | grep -vi "br-" | grep -vi "service" | sed -r "s/.* *UP *(.*) /\1/g" | cut -d " " -f 1 | grep -v ":" | grep "/24")
EXTERNAL_IP2=$(ip -br a | grep "UNKNOWN" | grep -vi "br-" | grep -vi "service" | sed -r "s/.* *UNKNOWN *(.*) /\1/g" | cut -d " " -f 1 | grep -v ":" | grep "/24")

if [ -z $EXTERNAL_IP2 ]; then
    export EXTERNAL_IP=$EXTERNAL_IP1
else
    export EXTERNAL_IP=$EXTERNAL_IP2
fi


exec fastapi run main.py --host 127.0.0.1 --port 8000 --forwarded-allow-ips="127.0.0.1" --root-path /api