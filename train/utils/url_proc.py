import re
spec_chars = '[@_!#$%^&*()<>?/|}{~:]'


def gen_url_info(url: str):
    url_len = len(url)
    num_digits = 0
    num_spec_chars = 0
    num_nalpha_chars = 0
    num_payload_args = 0
    payload = get_payload_from_url(url)
    if payload:
        num_payload_args = len(get_payload_args(payload))
    for c in url:
        if not c.isalpha():
            num_nalpha_chars += 1
        if c.isdigit():
            num_digits += 1
        if c in spec_chars:
            num_spec_chars += 1
    return url_len, num_digits, num_spec_chars, num_nalpha_chars, num_payload_args


def gen_payload_info(payload: str):
    num_digits = 0
    num_spec_chars = 0
    num_nalpha_chars = 0
    num_payload_args = len(get_payload_args(payload))
    for c in payload:
        if not c.isalpha():
            num_nalpha_chars += 1
        if c.isdigit():
            num_digits += 1
        if c in spec_chars:
            num_spec_chars += 1
    return num_digits, num_spec_chars, num_nalpha_chars, num_payload_args


def gen_content_info(content: str):
    if content is np.nan:
        return tuple([0]*5)
    c_len = len(content)
    c_num_digits = 0
    c_num_spec_chars = 0
    c_num_nalpha_chars = 0
    c_num_payload_args = len(get_payload_args(content))
    for c in content:
        if not c.isalpha():
            c_num_nalpha_chars += 1
        if c.isdigit():
            c_num_digits += 1
        if c in spec_chars:
            c_num_spec_chars += 1
    return c_len, c_num_digits, c_num_spec_chars, c_num_nalpha_chars, c_num_payload_args


def get_payload_from_url(url: str):
    i = url.find('?')
    if i==-1:
        return None
    return url[i+1:]


def get_payload_args(payload: str):
    return re.findall('(\S+?=\S+?)[& ]', payload)