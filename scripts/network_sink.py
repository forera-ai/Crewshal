"""Bounded local echo/data sink, independently observed by the coordinator."""

import json
from pathlib import Path
import select
import socket
import time


def main() -> None:
    sockets = {}
    for family in (socket.AF_INET, socket.AF_INET6):
        for kind, port in (
            (socket.SOCK_STREAM, 18080),
            (socket.SOCK_DGRAM, 18080),
            (socket.SOCK_DGRAM, 15353),
        ):
            connection = socket.socket(family, kind)
            if family == socket.AF_INET6:
                connection.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
            connection.bind(("0.0.0.0" if family == socket.AF_INET else "::", port))
            if kind == socket.SOCK_STREAM:
                connection.listen(4)
            sockets[connection] = (family, kind, port)
    stop = time.monotonic() + 60
    with Path("/candidate/owned/events.jsonl").open("w", buffering=1) as events:
        Path("/candidate/owned/heartbeat").write_text(str(time.monotonic()))
        Path("/candidate/owned/ready").write_text("ready")
        while time.monotonic() < stop:
            Path("/candidate/owned/heartbeat").write_text(str(time.monotonic()))
            readable, _, _ = select.select(list(sockets), [], [], 0.05)
            for connection in readable:
                family, kind, port = sockets[connection]
                if kind == socket.SOCK_STREAM:
                    with connection.accept()[0] as client:
                        client.settimeout(0.2)
                        data = client.recv(4096)
                        client.sendall(data)
                else:
                    data, peer = connection.recvfrom(4096)
                    connection.sendto(data, peer)
                events.write(
                    json.dumps(
                        {
                            "family": "ipv4" if family == socket.AF_INET else "ipv6",
                            "protocol": "dns"
                            if port == 15353
                            else "tcp"
                            if kind == socket.SOCK_STREAM
                            else "udp",
                            "payload_hex": data.hex(),
                        }
                    )
                    + "\n"
                )


if __name__ == "__main__":
    main()
