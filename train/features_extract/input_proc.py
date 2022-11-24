import re
import numpy as np
spec_chars = '[@_!#$%^&*()<>?/|}{~:]'
url_regex = '([^ "]+)? HTTP/[0-9.]+'
start = len('http://localhost:8080')

# Example http://localhost:8080/tienda1/publico/anadir.jsp HTTP/1.1 -> page: /tienda1/publico/anadir.jsp
def gen_url_info(url: str):
    url = re.match(url_regex, url).group(1)
    page = url[start:]
    url_len = len(page)
    num_digits = 0
    num_spec_chars = 0
    num_nalpha_chars = 0
    num_payload_args = 0
    payload = get_payload(page)
    if payload:
        num_payload_args = len(get_payload_args(payload))
    for c in page:
        if not c.isalpha():
            num_nalpha_chars += 1
        if c.isdigit():
            num_digits += 1
        if c in spec_chars:
            num_spec_chars += 1
    return url_len, num_digits, num_spec_chars, num_nalpha_chars, num_payload_args

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

def get_payload(url: str):
    i = url.find('?')
    if i==-1:
        return None
    return url[i+1:]

def get_payload_args(payload: str):
    return re.findall('(\S+?=\S+?)[& ]', payload)