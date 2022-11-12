#!/usr/bin/python3
import struct
import socket
import websocket as ws

HOST = "0.0.0.0"
PORT = 5555
BUF_SIZE = 4096
HDR_SIZE = 4
ACK_MSG = b"<|ACK|>"
logfile = open("output.txt", "w")


def createSocket():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((HOST, PORT))
	return sock


def storeLogs(loglines):
	logfile.writelines(loglines)
	logfile.flush()


def listen(sock):
	sock.listen(1)
	print("Server listening on port", PORT)
	c, addr = sock.accept()
	print("Connect from ", str(addr))
	handleClient(c)
	logfile.close()


def handleClient(con):
	while True:
		chunk = con.recv(HDR_SIZE)
		if chunk == b'':
			print("Client disconnected.")
			break
		(length,) = struct.unpack('>L', chunk)
		data = b''
		while len(data) < length:
			to_read = length - len(data)
			data += con.recv(min(to_read, BUF_SIZE))

		print("Received", len(data), "bytes.")
		loglines = data.decode().split("<br>")
		# ws.sendLogs(loglines)
		storeLogs(loglines)
		con.send(ACK_MSG)


if __name__ == "__main__":
	sock = createSocket()
	listen(sock)
