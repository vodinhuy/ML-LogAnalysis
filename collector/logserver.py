import struct
import socket
import websocket as ws

HOST = "0.0.0.0"
PORT = 5555
BUF_SIZE = 4096


def createSocket():
	sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sck.bind((HOST, PORT))
	return sck


def run(sck):
	sck.listen(1)
	print("Server listening on port", PORT)

	c, addr = sck.accept()
	print("Connect from ", str(addr))

	while True:
		bs = c.recv(8)
		(length,) = struct.unpack('>Q', bs)
		data = b''
		while len(data) < length:
			to_read = length - len(data)
			data += c.recv(min(to_read, BUF_SIZE))

		assert len(b'\00') == 1
		c.sendall(b'\00')
		print("Received", len(data), "bytes.")
		loglines = data.decode().split("<br>")
		ws.sendLogs(loglines)


if __name__ == "__main__":
	sck = createSocket()
	run(sck)
