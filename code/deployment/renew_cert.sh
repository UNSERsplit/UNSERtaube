#!/bin/sh

mkdir -p /app/cert
cd /app/cert

openssl req -x509 -nodes -days 365 \
 -newkey rsa:2048 \
 -keyout /app/cert/cert.key \
 -out /app/cert/cert.crt \
 -config /app/deployment/cert.cnf

nginx -s reload