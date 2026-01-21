FROM python:3.8-slim


# Install nginx and sftp
RUN mkdir -p /app && apt update && apt install -y --no-install-recommends --no-install-suggests nginx openssh-client

WORKDIR /app

# install backend requirements
COPY ./backend/requirements.txt ./backend/requirements.txt
RUN pip install -r ./backend/requirements.txt

# copy entrypoint
COPY ./deployment/start.sh ./deployment/renew_cert.sh ./

# copy nginx configuration
COPY ./deployment/nginx.conf /etc/nginx/nginx.conf

# copy backend
COPY ./backend ./backend

# dns from dnsmasq
#EXPOSE 53/udp
# web
EXPOSE 80/tcp
EXPOSE 443/tcp

ENTRYPOINT ["/app/start.sh"]
