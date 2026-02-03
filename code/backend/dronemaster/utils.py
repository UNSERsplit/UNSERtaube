from typing import Optional

def find_mac(ip: str) -> Optional[str]:
    with open("/proc/net/arp", "r") as f:
        for line in f.readlines():
            if line.startswith(ip):
                return line[41:41+17]
    return None