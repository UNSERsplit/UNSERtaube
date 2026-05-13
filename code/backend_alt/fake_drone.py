import socket
import threading
import time

def receiving_thread():
    global last_addr, is_in_setup
    while True:
        msg, addr = s.recvfrom(1024)
        if addr != last_addr:
            is_in_setup = True
        last_addr = addr

        if is_in_setup:
            if msg.startswith(b"EXT led"):
                s.sendto(b"led ok", addr)
                is_in_setup = False
            else:
                s.sendto(b"ok", addr)
        else:
            print(msg)

def state_thread():
    global last_addr
    data = b"mid:0;pitch:1;roll:2;yaw:3;vgx:0;vgy:0;vgz:0;bat:99;templ:50;temph:60;tof:35;h:0;time:0;agx:0.00;agy:0.00;agz:0.00;baro:150.0"
    while last_addr is None:
        pass
    while True:
        assert last_addr is not None
        s.sendto(data, last_addr)
        time.sleep(0.1)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 8889))

is_in_setup = True
last_addr = None

t = threading.Thread(target=receiving_thread)
t.start()

ts = threading.Thread(target=state_thread)
ts.start()


try:
    while True:
        i = input()
        if i == "exit":
            break
        assert last_addr is not None
        s.sendto(i.encode(), last_addr)
finally:
    s.close()
    t.join()
    ts.join()