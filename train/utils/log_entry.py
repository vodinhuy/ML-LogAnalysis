import re
from . import url_proc
spec_chars = '[@_!#$%^&*()<>?/|}{~:]'
#log_regex = '^(\S+) \S+ (\S+) \[([^\]]+)\] "([A-Z]+) ([^ "]+)? HTTP/[0-9.]+" ([0-9]{3}) ([0-9]+|-)'
log_regex = '^(\S+) \S+ (\S+) \[([^\]]+)\] "([A-Z]+) ([^ "]+)? HTTP/[0-9.]+" ([0-9]{3}) ([0-9]+|-) "([^"]*)" "([^"]*)"'
'''
    Groups:
    0: Ip address
    1: logname
    2: Date and Time zone
    3: Page access method
    4: Path of requested file
    5: Server response code
    6: Bytes received
    7: Referrer url
    8: User agent
'''
d_methods = {'POST': 0, 'GET': 1, 'PUT': 2}


'''
    extract_info
    Params: str - log_entry
    Returns: Data fields in log_entry
'''
def split(log_entry):
    m = re.match(log_regex, log_entry)
    if m:
        return m.groups()
    return None

'''
    convert_data
    Returns:
    method_num, host_num, *content_length*, url_len, digits, spec_chars, not_alpha_chars, payload_args
    ext* : c_len, c_digits, c_spec_chars, c_not_alpha_chars, c_payload_args
'''
def extract_info(log_entry):
    info = split(log_entry)
    if info:
        method_num = d_methods.get(info[3],0)
        host_num = 0
        url_info = url_proc.gen_url_info(info[4]) # tuple : url_len, num_digits, num_spec_chars, num_nalpha_chars, num_payload_args
        return tuple([method_num, host_num]) + url_info
    return None

def get_input_test(log_entry):
    info = split(log_entry)
    if info:
        payload = url_proc.get_payload_from_url(info[4])
        if payload:
            payload_info = tuple([len(payload)]) + url_proc.gen_payload_info(payload) # tuple : num_digits, num_spec_chars, num_nalpha_chars, num_payload_args
            return payload_info
    return None


if __name__ == '__main__':
    # print(extract_info('127.0.0.1 - jg [27/Apr/2012:11:27:36 +0700] "GET /regexcookbook.html HTTP/1.1" 200 2326'))
    while True:
        s = input('INPUT:')
        print(extract_info(s))
