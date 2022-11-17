import re
import numpy as np

spec_chars = '[@_!#$%^&*()<>?/|}{~:]'
#log_regex = '^(\S+) \S+ (\S+) \[([^\]]+)\] "([A-Z]+) ([^ "]+)? HTTP/[0-9.]+" ([0-9]{3}) ([0-9]+|-)'
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
d_methods = {'POST': 0, 'GET': 1, 'PUT': 2}


def _split(entry):
    m = re.match(common_log_regex, entry)
    if m:
        return m.groups()
    return None


def _list_payload_args(payload: str):
    return re.findall('(\S+?=\S+?)[& ]', payload)


def _gen_payload_info(payload: str):
    num_digits = 0
    num_spec_chars = 0
    num_nalpha_chars = 0
    num_payload_args = len(_list_payload_args(payload))
    for c in payload:
        if not c.isalpha():
            num_nalpha_chars += 1
        if c.isdigit():
            num_digits += 1
        if c in spec_chars:
            num_spec_chars += 1
    return num_digits, num_spec_chars, num_nalpha_chars, num_payload_args


def _payload_from_url(url: str):
    i = url.find('?')
    if i == -1:
        return None
    return url[i+1:]


# def _gen_content_info(content: str):
#     if content is np.nan:
#         return tuple([0]*5)
#     c_len = len(content)
#     c_num_digits = 0
#     c_num_spec_chars = 0
#     c_num_nalpha_chars = 0
#     c_num_payload_args = len(_list_payload_args(content))
#     for c in content:
#         if not c.isalpha():
#             c_num_nalpha_chars += 1
#         if c.isdigit():
#             c_num_digits += 1
#         if c in spec_chars:
#             c_num_spec_chars += 1
#     return c_len, c_num_digits, c_num_spec_chars, c_num_nalpha_chars, c_num_payload_args


def _gen_url_info(url: str):
    url_len = len(url)
    num_digits = 0
    num_spec_chars = 0
    num_nalpha_chars = 0
    num_payload_args = 0
    payload = _payload_from_url(url)
    if payload:
        num_payload_args = len(_list_payload_args(payload))
    for c in url:
        if not c.isalpha():
            num_nalpha_chars += 1
        if c.isdigit():
            num_digits += 1
        if c in spec_chars:
            num_spec_chars += 1
    return url_len, num_digits, num_spec_chars, num_nalpha_chars, num_payload_args


def extract_info(log_entry: str):
    '''
    Returns:
        method_num, host_num, *content_length*, url_len, digits, spec_chars, not_alpha_chars, payload_args
        ext* : c_len, c_digits, c_spec_chars, c_not_alpha_chars, c_payload_args
    '''
    info = _split(log_entry)
    if not info:
        return None
    method_num = d_methods.get(info[3], 0)
    host_num = 0
    # tuple : url_len, num_digits, num_spec_chars, num_nalpha_chars, num_payload_args
    return tuple([method_num, host_num]) + _gen_url_info(info[4])


def get_input_test(log_entry: str):
    info = _split(log_entry)
    if not info:
        return None
    payload = _payload_from_url(info[4])
    if payload:
        # tuple : num_digits, num_spec_chars, num_nalpha_chars, num_payload_args
        return tuple([len(payload)]) + _gen_payload_info(payload)
