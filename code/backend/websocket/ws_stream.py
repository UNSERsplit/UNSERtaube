import socket

video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
video_socket.bind(('0.0.0.0', 11111))

frontend_forwarding = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def listenToStream(reciever_socket, stop_stream_event):
    pass # TODO
    #while not stop_stream_event.is_set():
    #    data, addr = video_socket.recvfrom(4096)
    #    frontend_forwarding.sendto(data, reciever_socket)
    #frontend_forwarding.close()
    #video_socket.close()
