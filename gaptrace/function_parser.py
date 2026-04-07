import re

def extract_functions(code: str):
    pattern = r'\b(\w+)\s+(\w+)\((.*?)\)\s*{'
    matches = re.findall(pattern, code)

    functions = []
    for ret_type, name, args in matches:
        functions.append({
            "return_type": ret_type,
            "name": name,
            "args": args
        })

    return functions