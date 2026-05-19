#!/bin/sh


sftp -i ./taube_rsa -o "StrictHostKeyChecking no" taube@unser.dns64.de:/etc/letsencrypt/live/taube.unser.dns64.de/privkey.pem privkey.pem
sftp -i ./taube_rsa -o "StrictHostKeyChecking no" taube@unser.dns64.de:/etc/letsencrypt/live/taube.unser.dns64.de/fullchain.pem fullchain.pem
