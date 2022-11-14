#!/usr/bin/python3

import sys
import socket
import selectors
import traceback
import json

import libclient
import io

sel = selectors.PollSelector()


def start_connection(**kwargs):
    addr = (kwargs["host"], kwargs["port"])
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, **kwargs)
    sel.register(sock, events, data=message)


# if len(sys.argv) != 5:
#     print(f"Usage: {sys.argv[0]} <host> <port> <access-log>")
#     sys.exit(1)

# host, port = sys.argv[1], int(sys.argv[2])
# action, value = sys.argv[3], sys.argv[4]

with open("config.json", "r") as f:
    config = json.load(f)

name = config.get("NAME", "unnamed-node")
host = config.get("LOG_SERVER", "127.0.0.1")
port = config.get("SERVER_PORT", 5555)
log_path = config.get("ACCESS_LOG_PATH", "")
print("NAME:", config.get("NAME"))
print("HOST:", config.get("LOG_SERVER"))
print("PORT:", config.get("SERVER_PORT"))
print("ACCESS LOG:", config.get("ACCESS_LOG_PATH"))
start_connection(**dict(name=name, host=host, port=port, log_path=log_path))

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            if isinstance(key.fileobj, io.TextIOWrapper):
                lw = key.data
                lw.process_read_event(mask)
            else:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        f"Main: Error: Exception for {message.addr}:\n"
                        f"{traceback.format_exc()}"
                    )
                    message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            print("Soket closed")
            break
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
