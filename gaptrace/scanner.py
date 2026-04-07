from pathlib import Path
from gaptrace.function_parser import extract_functions
from gaptrace.test_parser import extract_tests


def classify_files(files):
    source = []
    tests = []

    for f in files:
        name = f.name.lower()

        if "test" in name:
            tests.append(f)
        else:
            source.append(f)

    return source, tests


def read_files(files):
    combined = ""
    for f in files:
        try:
            combined += f.read_text(errors="ignore") + "\n"
        except:
            pass
    return combined


def scan_project(path):
    path = Path(path)

    # Support multiple C/C++ file extensions
    cpp_extensions = ["*.cpp", "*.cc", "*.cxx", "*.c", "*.h", "*.hpp", "*.hxx"]
    cpp_files = []
    for ext in cpp_extensions:
        cpp_files.extend(path.rglob(ext))

    source, tests = classify_files(cpp_files)

    print(f"\nSource files: {len(source)}")
    print(f"Test files: {len(tests)}")

    source_code = read_files(source)
    test_code = read_files(tests)

    functions = extract_functions(source_code)

    print(f"\nDetected functions: {len(functions)}")
    for f in functions:
        print(f" - {f['name']}({f['args']})")

    print("\n⚠️  Note: For accurate gap analysis, use 'gaptrace parse --src <file>'")
    print("   which uses AST-based analysis instead of heuristics.")