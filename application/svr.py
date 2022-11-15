import socket
import selectors
import traceback
import json

import server.libserver as libserver
import utils.dbutil as dbutil
import utils.websocket as ws
import utils.logparser as logparser


class EventHandler:
    def __init__(self) -> None:
        self.db = dbutil.get_database()

    def process_data(self, pkg):
        docs = []
        # client_name = pkg["client"]
        loglines = pkg["data"].split("<br>")
        for line in loglines:
            docs.append(logparser.parse(line))
        res = dbutil.insertDocs(self.db["weblogs"], docs)
        print(f"{len(res)} docs inserted.")


class LogServer:
    def __init__(self, config_file) -> None:
        self.selector = selectors.DefaultSelector()
        self.event_handler = EventHandler()
        with open(config_file, "r") as f:
            self.config = json.load(f)

        host, port = (self.config.get("SERVER_HOST", "0.0.0.0"),
                      self.config.get("SERVER_PORT", 5555))

        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, port))
        lsock.listen()
        print(f"Listening on {(host, port)}")
        lsock.setblocking(False)
        self.selector.register(lsock, selectors.EVENT_READ, data=None)
        dbutil.deleteAll(dbutil.get_database()["weblogs"])

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        message = libserver.Message(
            self.selector, conn, addr, self.config, event_handler=self.event_handler)
        self.selector.register(conn, selectors.EVENT_READ, data=message)

    def run_loop(self):
        try:
            while True:
                events = self.selector.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
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
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self.selector.close()
