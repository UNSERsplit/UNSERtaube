#! /bin/bash
 
gnome-terminal -- ./mediamtx
gnome-terminal -- ./start_ffmpeg.sh

fastapi dev main.py
