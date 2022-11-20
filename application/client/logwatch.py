import threading
import selectors
import time


class LogWatcher:
    def __init__(self, sel, callback, log_path, interval) -> None:
        self.selector = sel
        self.callback = callback
        self.interval = interval
        self.logfile = open(log_path, "r")
        self._running = False
        self._thread = threading.Thread(target=self._watchdog, daemon=True)
        self._send_blocked = False
        self.loglines = []
        self.lock = threading.Lock()

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()
        self.logfile.close()

    def _read_to_end(self):
        while True:
            line = self.logfile.readline()
            if not line:
                break
            yield line

    def _read_lines(self, n_lines):
        i = 0
        while i < n_lines:
            line = self.logfile.readline()
            if not line:
                break
            yield line
            i += 1

    def _read(self):
        lines = self._read_lines(100)
        self.loglines.extend(lines)

        if len(self.loglines) > 0:
            if self._send_blocked:
                return
            if not self.selector.get_map().get(self.logfile):
                self.selector.register(
                    self.logfile, selectors.EVENT_READ, self)
            print(f"Read {len(self.loglines)} lines from log file.")

    def _watchdog(self):
        while self._running:
            with self.lock:
                self._read()
            time.sleep(self.interval)

    def process_read_event(self, mask):
        if mask & selectors.EVENT_READ:
            with self.lock:
                self._send_blocked = True
                chunk = "<br>".join(self.loglines)
                self.loglines = []
                print(f"Send {len(chunk)} bytes of logs.")
                self.selector.unregister(self.logfile)
                self.callback(chunk)

    def nofify_done(self):
        self._send_blocked = False
