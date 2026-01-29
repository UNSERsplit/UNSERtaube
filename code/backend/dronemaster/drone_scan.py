from threading import Thread
import socket
import ipaddress
import asyncio
from typing import Coroutine, Any, Callable
import time


def scan(ip_cidr: str, callback: Callable[[tuple[str, int]], Coroutine[Any, Any, None]], close_callback: Callable[[], Coroutine[Any, Any, None]]):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(20)
    sock.bind(('0.0.0.0', 8890))

    t = start_receive_task(sock, callback, close_callback)
    send_requests(sock, ip_cidr)
    t.join()
    return

def start_receive_task(sock: socket.socket, callback: Callable[[tuple[str, int]], Coroutine[Any, Any, None]], close_callback: Callable[[], Coroutine[Any, Any, None]]):
    t = Thread(target=_receive_task, args=(sock,callback, close_callback))
    t.start()
    return t

def _receive_task(sock: socket.socket, callback: Callable[[tuple[str, int]], Coroutine[Any, Any, None]], close_callback: Callable[[], Coroutine[Any, Any, None]]):
    t = time.time()
    while True:
        try:
            resp, addr = sock.recvfrom(1024)
            if resp.upper() == b"OK":
                t = time.time()
                asyncio.run(callback(addr))
                sock.sendto(b"motoroff", addr)
            else:
                if time.time() - t > 10:
                    break
                #print(f"unknown response: '{resp}' from {addr}")
        except socket.timeout:
            print("Timeout")
            break
    sock.close()
    asyncio.run(close_callback())

def send_requests(sock: socket.socket, ip_cidr: str):
    for ip in ipaddress.IPv4Network(ip_cidr):
        if str(ip).split(".")[-1] in ("255", "0"):
            continue
        sock.sendto(b"command", (str(ip), 8889))
