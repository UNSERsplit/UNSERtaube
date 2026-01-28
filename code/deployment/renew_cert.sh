#!/bin/sh

mkdir -p /app/cert
cd /app/cert

sftp -i /credentials/taube_rsa -o "StrictHostKeyChecking no" taube@unser.dns64.de:/etc/letsencrypt/live/taube.unser.dns64.de/privkey.pem privkey.pem
sftp -i /credentials/taube_rsa -o "StrictHostKeyChecking no" taube@unser.dns64.de:/etc/letsencrypt/live/taube.unser.dns64.de/fullchain.pem fullchain.pem

#nginx -s reload