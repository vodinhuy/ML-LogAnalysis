import sys
import selectors
import json
import io
import struct
import logwatch


class Message:
    def __init__(self, selector, sock, addr, **kwargs):
        self.server_connected = False
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.client_name = kwargs["name"]
        self.log_path = kwargs["log_path"]
        # self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self._config_loaded = False
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None
        self.configuration = None

    def _set_selector_events_mask(self, mode):
        print(f"set_selector_events_mask: {mode}")
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {mode!r}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            if len(self._send_buffer) <= 1000:
                print(
                    f"Sending {self._send_buffer!r} ({len(self._send_buffer)} bytes) to {self.addr}")
            else:
                print(f"Sending {len(self._send_buffer)} bytes to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_request(self, request_type):
        if request_type == "configuration":
            request = {
                "type": "text/json",
                "encoding": "utf-8",
                "content": dict(action="config-sync")
            }
        else:
            request = {}

        content = request["content"]
        content_type = request["type"]
        content_encoding = request["encoding"]
        if content_type == "text/json":
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        return req

    def _create_post(self, content):
        content_encoding = "utf-8"
        return {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/data",
            "content_encoding": content_encoding,
        }

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _process_response_json_content(self):
        content = self.response
        result = content.get("result")
        if content.get("request_type") == "config-sync":
            self._config_loaded = True
            self.configuration = result
            print(f"Configuration: {result}")
            print("Starting log watcher ...")
            self.start_log_watcher()
        else:
            print(f"Got result: {result}")

    def _process_response_binary_content(self):
        content = self.response
        print(f"Got response: {content!r}")

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()
        self.process_protoheader()
        self.process_jsonheader()
        self.process_response()

    def write(self):
        if not self._config_loaded:
            self.send_request("configuration")
            self._write()
            self._set_selector_events_mask("r")
        else:
            self._write()

    def close(self):
        print(f"Closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"Error: selector.unregister() exception for "
                f"{self.addr}: {e!r}"
            )

        try:
            self.sock.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.addr}: {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def send_request(self, request_type):
        # content = self.request["content"]
        # content_type = self.request["type"]
        # content_encoding = self.request["encoding"]
        req = self._create_request(request_type)
        message = self._create_message(**req)
        self._send_buffer += message

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f"Missing required header '{reqhdr}'.")

    def process_response(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.response = self._json_decode(data, encoding)
            print(f"Received response {self.response!r} from {self.addr}")
            self._process_response_json_content()
        else:
            # Binary or unknown content-type
            self.response = data
            print(
                f"Received {self.jsonheader['content-type']} "
                f"response from {self.addr}"
            )
            self._process_response_binary_content()
        # Close when response has been processed
        # self.close()

    def start_log_watcher(self):
        interval = self.configuration.get("SEND_INTERVAL", 1)
        self.logw = logwatch.LogWatcher(
            self.selector, self.send_logs, self.log_path, interval)
        self.selector.register(self.logw.logfile, selectors.EVENT_READ,
                               data=self.logw)
        self.logw.start()

    def send_logs(self, log_data):
        if not log_data:
            return

        content = {
            "client": self.client_name,
            "data": log_data
        }
        req = self._create_post(content)
        message = self._create_message(**req)
        self._send_buffer += message
        self._set_selector_events_mask("w")
