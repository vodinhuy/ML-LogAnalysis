import re

common_log_regex = '^(\S+) \S+ (\S+) \[([^\]]+)\] "([A-Z]+) ([^ "]+)? (HTTP/[0-9.]+)" ([0-9]{3}) ([0-9]+|-) "([^"]*)" "([^"]*)"'


def _split(entry):
	m = re.match(common_log_regex, entry)
	if m:
		return m.groups()
	return None


def parse(row):
	vals = _split(row)
	if not vals:
		return None
	res = {
		'ip': vals[0],
		'time': vals[2],
		'method': vals[3],
		'data': vals[4],
		'protocol': vals[5],
		'status': vals[6],
		'ua': vals[9]
	}
	return res
