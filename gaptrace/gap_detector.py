def has_zero_test(test_code: str):
    patterns = ["(0", ", 0", " 0)"]
    return any(p in test_code for p in patterns)


def detect_division_gaps(functions, source_code, test_code):
    gaps = []

    for func in functions:
        name = func["name"]

        if "/" in source_code:
            if not has_zero_test(test_code):
                gaps.append({
                    "function": name,
                    "issue": "Missing division by zero",
                    "why": "Function performs division but no test uses denominator = 0"
                })

    return gaps