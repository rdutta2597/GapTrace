import re

def extract_tests(code: str):
    pattern = r'TEST.*?\((.*?)\)'
    return re.findall(pattern, code)