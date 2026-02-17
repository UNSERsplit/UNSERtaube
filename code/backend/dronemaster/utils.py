from typing import Optional
from sys import stderr

def find_mac(ip: str) -> Optional[str]:
    with open("/proc/net/arp", "r") as f:
        for line in f.readlines():
            if line.startswith(ip):
                return line[41:41+17]
    return None

def log(*args):
    print(*args, file=stderr)
    stderr.flush()