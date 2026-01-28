FROM node:25-alpine AS frontend-build

WORKDIR /build

COPY ./frontend/package.json ./frontend/*package-lock.json* ./

RUN --mount=type=cache,target=/root/.npm npm ci

COPY ./frontend .

RUN npm run build 

FROM python:3.13-slim


# Install nginx and sftp
RUN mkdir -p /app && apt update && apt install -y --no-install-recommends --no-install-suggests nginx openssh-client curl

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

# copy frontend
COPY --chown=www-data:www-data --from=frontend-build /build/dist/frontend/browser ./frontend

STOPSIGNAL SIGINT

# web
EXPOSE 80/tcp
EXPOSE 443/tcp
EXPOSE 8890/udp
EXPOSE 11111/udp

ENTRYPOINT ["/app/start.sh"]
