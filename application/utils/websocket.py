import os
import struct
import json
import select
import threading
import traceback
from . import dbadapter

msg_types = {
    1: "text",
    2: "binary",
    8: "client_connected",
    16: "client_info"
}

commands = ["load_logs"]
fields = ["ip", "time", "method", "data", "protocol", "ua"]


class WebSocket:
    def __init__(self, dba: dbadapter.DBAdapter) -> None:
        self.dba = dba
        self._thread = threading.Thread(target=self._recv_data, daemon=True)
        self._thread.start()
        self.client_list = {}

    def _send_msg(self, msg, clientid=0):
        fifo = open("/tmp/wspipein.fifo", "wb")
        # Send the header packed as an unsigned long (32-bit) in network (big-endian) order.
        # 0 -> Broadcast to all clients. You may specify the client id.
        # 1 -> Message type. 2 -> binary, 1 -> text
        fifo.write(struct.pack(">LLL", clientid, 1, len(msg)))
        # Followed by a second write containing the payload
        fifo.write(msg)
        fifo.close()

    def _recv_data(self):
        poller = select.poll()
        fifo = os.open("/tmp/wspipeout.fifo", os.O_RDONLY | os.O_NONBLOCK)

        poller.register(fifo, select.POLLIN)
        while True:
            try:
                p = poller.poll()
                hdr = os.read(p[0][0], 12)
                if len(hdr):
                    listener, mtype, size, = struct.unpack('>LLL', hdr)
                print(f"[WS] client: {listener}, mtype: {mtype}, size: {size}")
                buf = os.read(p[0][0], size)
                if len(buf):
                    print(f">msg: {buf}")

                self.process_message(listener, mtype, buf.decode())
            except Exception as e:
                traceback.print_exc()

    def _log_items(self, docs):
        res = []
        for doc in docs:
            res.append(dict((f, doc[f]) for f in fields))
        return res

    def _json_encode(self, obj):
        return json.dumps(obj).encode("utf-8")

    def process_message(self, clientid, mtypeid, msg):
        mtype = msg_types.get(mtypeid)
        if not mtype:
            print("Invalid message type:", mtypeid)
            return

        if mtype == "client_connected":
            if self.client_list.get(clientid):
                self.client_list.pop(clientid)
                print(f">client {clientid} disconnected")
            else:
                self.client_list[clientid] = {"ip": None}
                print(f">client {clientid} connected")
        elif mtype == "client_info":
            ip_addr = msg[:msg.find("\x00")+1]
            self.client_list[clientid] = {"ip": ip_addr}
            print(f">client {clientid} - IP: {ip_addr}")
        elif mtype == "text":
            self.process_client_commands(clientid, msg)
        else:
            pass

    def process_client_commands(self, clientid, cmd):
        if not cmd in commands:
            return
        print(f"[CMD] <{cmd}> from client {clientid}")
        if cmd == "load_logs":
            docs = self.dba.find_all("weblogs")
            items = self._log_items(docs)
            self._send_msg(self._json_encode(items), clientid)
            print(f"<Send> {len(items)} log records to client {clientid}")
        else:
            pass

    def send_logs(self, docs):
        items = self._log_items(docs)
        self._send_msg(self._json_encode(items))
