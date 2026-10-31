#!/usr/bin/env python3
"""Send a WoL magic packet from a trusted Android Termux device on the PC LAN.

The destination Ethernet MAC address is read from TARGET_MAC in the PHONE'S
private environment; it is deliberately never part of the public repository.
Uses only Python's standard library.
"""

from __future__ import annotations

import argparse
import ipaddress
import os
import re
import socket


def normalize_mac(value: str) -> bytes:
    """Parse a 48-bit MAC, with colon, hyphen or no delimiters."""
    cleaned = re.sub(r"[:-]", "", value.strip())
    if not re.fullmatch(r"[0-9a-fA-F]{12}", cleaned):
        raise ValueError("TARGET_MAC must be a 12-digit hexadecimal Ethernet MAC address")
    return bytes.fromhex(cleaned)


def make_magic_packet(mac: str) -> bytes:
    """WoL payload = 6 FF bytes followed by 16 copies of the target MAC."""
    address = normalize_mac(mac)
    return b"\xff" * 6 + address * 16


def send_packet(mac: str, destination: str, port: int) -> None:
    """Broadcast a packet on the local LAN; do not expose this service publicly."""
    ipaddress.IPv4Address(destination)  # validate; no arbitrary DNS lookups
    if not 1 <= port <= 65535:
        raise ValueError("UDP port must be between 1 and 65535")
    packet = make_magic_packet(mac)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (destination, port))


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a LAN Wake-on-LAN magic packet")
    parser.add_argument("--mac", default=os.environ.get("TARGET_MAC", ""))
    parser.add_argument("--broadcast", default=os.environ.get("WOL_BROADCAST", "255.255.255.255"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("WOL_PORT", "9")))
    args = parser.parse_args()
    try:
        send_packet(args.mac, args.broadcast, args.port)
    except ValueError as exc:
        parser.error(str(exc))
    print("Wake-on-LAN magic packet sent on the local network (boot is not guaranteed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
