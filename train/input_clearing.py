import re
import numpy as np
spec_chars = '[@_!#$%^&*()<>?/|}{~:]'

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

def get_payload_args(payload: str):
    return re.findall('(\S+?=\S+?)[& ]', payload)