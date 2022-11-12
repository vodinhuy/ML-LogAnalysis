import os
import time
import socket
import struct

HOST = '127.0.0.1'
PORT = 8080
BUF_SIZE = 1024
interval = 0.5


def connect():
	sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sck.connect((HOST, PORT))
	return sck


def sendLogs(sck, logData):
	print("sendLogs", len(logData))
	if len(logData) == 0:
		return
	print("Sending log data:", len(logData))
	length = struct.pack('>L', len(logData))
	sck.sendall(length)
	sck.sendall(logData)
	# ack = sck.recv(1)
	# handle ack here


def readToEnd(inFile):
	while True:
		line = inFile.readline()
		if not line:
			break
		yield line

if __name__ == "__main__":
	logfile = open("../access_log.txt", "r")
	#logfile.seek(0, os.SEEK_END)
	loglines = readToEnd(logfile)
	sck = connect()
	for line in loglines:
		sendLogs(sck, line.strip().encode())
		time.sleep(interval)