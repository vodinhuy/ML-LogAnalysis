import socket
import struct

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
		bs = c.recv(4)
		(length,) = struct.unpack('>L', bs)
		data = b''
		while len(data) < length:
			to_read = length - len(data)
			data += c.recv(min(to_read, BUF_SIZE))

		assert len(b'\00') == 1
		c.sendall(b'\00')
		print("Received", len(data), "bytes.")
		writeLog(data)


def writeLog(data):
	outfile.write(data + b"\n")
	outfile.flush()


if __name__ == "__main__":
	with open("output2.txt", "wb") as outfile:
		sck = createSocket()
		run(sck)
