FROM alpine:latest
RUN apk add socat

EXPOSE 8443

ENTRYPOINT [ "socat",  "TCP-LISTEN:8443,fork,reuseaddr", "TCP:host.docker.internal:443" ]