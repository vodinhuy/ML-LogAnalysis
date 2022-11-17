import re

common_log_regex = '^(\S+) \S+ (\S+) \[([^\]]+)\] "([A-Z]+) ([^ "]+)? (HTTP/[0-9.]+)" ([0-9]{3}) ([0-9]+|-) "([^"]*)" "([^"]*)"'
'''
Groups:
    0: Ip address
    1: logname
    2: Date and Time zone
    3: Page access method
    4: Path of requested file
    5: HTTP version
    6: Server response code
    7: Bytes received
    8: Referrer url
    9: User agent
'''


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
