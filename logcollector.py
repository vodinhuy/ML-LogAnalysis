#!/usr/bin/python3
import os
import time
import socket
import struct

HOST = "192.168.88.130"
PORT = 5555
BUF_SIZE = 4096
HDR_SIZE = 4
ACK_MSG = b"<|ACK|>"
interval = 0.5


def connect():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	return sock


def sendLogs(sock, logData):
	print("Sending log data:", len(logData))
	sock.sendall(struct.pack('>L', len(logData)))
	sock.sendall(logData)
	ack = sock.recv(7)
	if ack == ACK_MSG:
		print("Received ACK from server")


def readToEnd(inFile):
	while True:
		line = inFile.readline()
		if not line:
			break
		yield line


def follow(inFile):
	inFile.seek(0, os.SEEK_END)
	while True:
		line = inFile.readline()
		if not line:
			time.sleep(0.1)
			continue
		yield line


if __name__ == "__main__":
	logfile = open("/var/log/httpd/access_log", "r")
	#logfile.seek(0, os.SEEK_END)
	loglines = readToEnd(logfile)
	sock = connect()
	msg = "<br>".join([line for line in loglines])
	sendLogs(sock, msg.encode())

	while True:
		newlines = readToEnd(logfile)
		msg = "<br>".join([line for line in newlines])
		if (len(msg) > 0):
			sendLogs(sock, msg.encode())

		time.sleep(interval)
