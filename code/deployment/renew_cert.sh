#!/bin/sh

mkdir -p /app/cert
cd /app/cert

sftp -i /app/ssh-key/taube_rsa taube@unser.dns64.de:/etc/letsencrypt/live/taube.unser.dns64.de/privkey.pem privkey.pem
sftp -i /app/ssh-key/taube_rsa taube@unser.dns64.de:/etc/letsencrypt/live/taube.unser.dns64.de/fullchain.pem fullchain.pem

nginx -s reload