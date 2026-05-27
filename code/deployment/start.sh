#!/bin/sh

BASE=$(dirname "$0")


cd $BASE

cd ..
deployment/renew_cert.sh

cd backend
gnome-terminal -- "./mediamtx"
gnome-terminal -- "./start_ffmpeg.sh"

gnome-terminal -- bash -c "uvicorn main:app --reload --port 8000 --host 0.0.0.0 --ssl-keyfile ../privkey.pem --ssl-certfile ../fullchain.pem && read -n 1 -p 'Press any key to continue'"

cd ../frontend
gnome-terminal -- sh -c "npm run start"

exit 1