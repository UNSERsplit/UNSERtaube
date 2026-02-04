# Installation
## 1. Get the docker image
you can use the published docker image `unserprojekt/taube:latest` \
or build it yourself from the `code` directory using `docker compose up --build`

## 2. Setup your env
copy `.env.example` as `.env` and change what you'd like

## 3. Get your ssh key
in order to get a valid certificate, you need a ssh certificate for noahs Hetzner server, you can find it in teams. \
Copy the `taube_rsa` key into the `code` directory, it is automatically mounted inside the docker container