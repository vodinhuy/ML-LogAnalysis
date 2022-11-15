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

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()

    def _readToEnd(self):
        i = 0
        while i < 50:
            line = self.logfile.readline()
            if not line:
                break
            yield line
            i += 1

    def _watchdog(self):
        while self._running:
            if not self.selector.get_map().get(self.logfile):
                self.selector.register(
                    self.logfile, selectors.EVENT_READ, self)
            time.sleep(self.interval)

    def process_read_event(self, mask):
        if mask & selectors.EVENT_READ:
            # chunk = self.logfile.read(4096)
            loglines = self._readToEnd()
            chunk = "<br>".join([line for line in loglines])

            if chunk:
                print(f"Read {len(chunk)} bytes from log file.")

            self.selector.unregister(self.logfile)
            self.callback(chunk)
