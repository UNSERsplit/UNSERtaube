from typing import Optional
from sys import stderr

def find_mac(ip: str) -> Optional[str]:
    with open("/proc/net/arp", "r") as f:
        for line in f.readlines():
            if line.startswith(ip):
                return line[41:41+17]
    return None

def log(level, *args):
    if level == "MSG" and len(args) >= 2 and str(args[1]).startswith("mid"):
        pass
        return
    if level == "MSG" and len(args) >= 3 and str(args[1]) == "???->S" and str(args[2]).startswith("mid"):
        pass
        return
    print(level, *map(lambda a: str(a).strip(), args), file=stderr)
    stderr.flush()