#ffmpeg -fflags nobuffer -flags low_delay -i udp://0.0.0.0:11111 -c:v libx264 -preset ultrafast -tune zerolatency -b:v 2M -c:a aac -b:a 128k -f rtsp -rtsp_transport udp rtsp://localhost:8554/camera

command="ffmpeg -fflags nobuffer -flags low_delay -i udp://0.0.0.0:11111 -c:v libx264 -preset ultrafast -tune zerolatency -b:v 2M -c:a aac -b:a 128k -f rtsp -rtsp_transport udp rtsp://localhost:8554/camera"

while [ 1 ]; do
    $command
    echo $?
    sleep 1
done


