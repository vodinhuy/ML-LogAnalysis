import os
import time
import socket
import struct

HOST = '192.168.88.130'
PORT = 5555
BUF_SIZE = 4096
interval = 1


def connect():
	sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sck.connect((HOST, PORT))
	return sck


def sendLogs(sck, logData):
	print("sendLogs", len(logData))
	if len(logData) == 0:
		return
	print("Sending log data:", len(logData))
	length = struct.pack('>Q', len(logData))
	sck.sendall(length)
	sck.sendall(logData)
	ack = sck.recv(1)
	# handle ack here


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
	sck = connect()
	msg = "<br>".join([line for line in loglines])
	sendLogs(sck, msg.encode())

	while True:
		newlines = readToEnd(logfile)
		msg = "<br>".join([line for line in newlines])
		sendLogs(sck, msg.encode())
		time.sleep(interval)
		assert sck.fileno() != -1
