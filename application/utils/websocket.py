import os
import struct
import json
from .logparser import parse


def sendLog(log):
	data = [parse(log)]
	_sendMsg(json.dumps(data))


def sendLogs(logs):
	data = []
	for logline in logs:
		data.append(parse(logline))

	_sendMsg(json.dumps(data))


def _sendMsg(msg):
	#msg = "Message to broadcast!"
	fifo = open("/tmp/wspipein.fifo", "wb")
	# Send the header packed as an unsigned long (32-bit) in network (big-endian) order.
	# 0 -> Broadcast to all clients. You may specify the client id.
	# 1 -> Message type. 2 -> binary, 1 -> text
	# Message length
	fifo.write(struct.pack(">LLL", 0, 1, len(msg)))
	# Followed by a second write containing the payload
	fifo.write(msg.encode())
	fifo.close()
