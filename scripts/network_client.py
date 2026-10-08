"""Frozen synthetic TCP/UDP/DNS-wire client; no provider or model calls."""

import json
from pathlib import Path
import platform
import socket
import struct
import sys


def packet(label: str, target: str, family: str, protocol: str) -> bytes:
    name = f"{label}.{target}.{family}.{protocol}.synthetic.invalid"
    if protocol == "dns":
        labels = b"".join(bytes([len(part)]) + part.encode() for part in name.split("."))
        return struct.pack("!6H", 0x2C01, 0x0100, 1, 0, 0, 0) + labels + b"\0\0\1\0\1"
    return name.encode()


def main() -> None:
    config = json.loads(Path("/input/targets.json").read_text())
    label = sys.argv[1]
    outcomes = []
    for target, addresses in config.items():
        for family, address in addresses.items():
            for protocol in ("tcp", "udp", "dns"):
                payload = packet(label, target, family, protocol)
                port = 15353 if protocol == "dns" else 18080
                kind = socket.SOCK_STREAM if protocol == "tcp" else socket.SOCK_DGRAM
                result = {
                    "target": target,
                    "family": family,
                    "protocol": protocol,
                    "payload_hex": payload.hex(),
                    "connected": False,
                    "sent": False,
                    "echo": False,
                }
                try:
                    with socket.socket(
                        socket.AF_INET if family == "ipv4" else socket.AF_INET6, kind
                    ) as connection:
                        connection.settimeout(0.2)
                        connection.connect((address, port))
                        result["connected"] = True
                        connection.sendall(payload)
                        result["sent"] = True
                        result["echo"] = connection.recv(4096) == payload
                except OSError as error:
                    result["error"] = type(error).__name__ + ": " + str(error)
                outcomes.append(result)
    Path("/candidate/owned/result.json").write_text(
        json.dumps(
            {
                "label": label,
                "outcomes": outcomes,
                "python": platform.python_version(),
                "kernel": platform.release(),
                "ipv6": socket.has_ipv6,
            }
        )
    )


if __name__ == "__main__":
    main()
