# 🔍 GapTrace

> **Coverage tells you what ran. GapTrace tells you what didn't — and why it matters.**

GapTrace is a developer-first CLI tool that detects **missing unit test scenarios** in C/C++ codebases by analyzing source code and comparing it against existing tests.

It doesn't generate tests.  
It exposes **logical blind spots** in your existing ones.

---

## 🚨 The Problem

You have:
- 85–95% code coverage ✅  
- All tests passing ✅  

And still:
- Edge cases break in production ❌  
- Failure paths go untested ❌  
- Assumptions silently fail ❌  

**Why?**

Because coverage tools answer:
"What lines were executed?"

But they don't answer:
"What important scenarios were never tested?"

---

## 💡 The GapTrace Approach

GapTrace flips the perspective:

Instead of asking "what is covered?"  
It asks 👉 "what logical paths are missing?"

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd GapTrace

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .
```

### Basic Usage

```bash
# Scan a directory for test gaps
gaptrace scan ./src

# Scan current directory
gaptrace scan .

# View help
gaptrace --help
gaptrace scan --help
```

### Example Output

```
Scanning project at: ./gaptrace/sample_project

Source files: 1
Test files: 1

Detected functions: 2
 - divide(int a, int b)
 - add(int x, y)

--- Gap Analysis ---
❌ divide: Missing division by zero
   Why: Function performs division but no test uses denominator = 0
```

---

## 📋 Current Features (v0.1.0)

### ✅ Implemented
- **C/C++ File Detection**: Scans `.cpp`, `.cc`, `.cxx`, `.c`, `.h`, `.hpp`, `.hxx` files
- **Function Extraction**: Identifies function signatures in source code
- **Test File Classification**: Separates source files from test files (files with "test" in name)
- **Division-by-Zero Detection**: Identifies functions with division operations but no zero-denominator tests
- **CLI Interface**: Easy-to-use command-line interface with subcommands

### 📌 Supported Test Frameworks
- **Google Test (gtest)**: Basic pattern detection

---

## 🔧 Architecture

```
gaptrace/
├── cli.py              # CLI entry point with subcommands
├── scanner.py          # Project scanning and file discovery
├── function_parser.py  # C/C++ function extraction
├── test_parser.py      # Test framework pattern detection
├── gap_detector.py     # Gap analysis engine
└── sample_project/     # Example C/C++ project for testing
```

---

## 🧪 Testing with Sample Project

```bash
# The repository includes a sample project
gaptrace scan gaptrace/sample_project

# Expected output: 2 functions detected, division-by-zero gap identified
```

---

## 🛠️ Tech Stack

- **Language**: Python 3.14+
- **CLI Framework**: Typer
- **Formatting**: Rich
- **Code Analysis**: Regex-based parsing (AST coming in Phase 2)

---

## 📈 Roadmap

### Phase 1 ✅ (Complete)
- [x] Basic CLI structure with subcommands
- [x] Multi-format C/C++ file detection
- [x] Function and test extraction
- [x] Division-by-zero gap detection

### Phase 2 (Next)
- [ ] AST-based parsing (replace regex patterns)
- [ ] Function-to-test mapping
- [ ] Additional gap detectors (null checks, bounds validation, error paths)
- [ ] Improved test framework support

### Phase 3 (Future)
- [ ] Risk scoring algorithm
- [ ] Detailed reports (JSON, HTML)
- [ ] Configuration file support

### Phase 4 (Vision)
- [ ] VS Code extension
- [ ] IDE integration
- [ ] Advanced analysis features

---

## ⚠️ Limitations (Current Version)

- Uses regex-based parsing (not AST-based yet)
- Limited gap detection (only division-by-zero)
- Basic test framework support
- No correlation between specific tests and functions
- C/C++ only (future: multi-language support)

---

## 📝 Development

This is an active development project. The codebase is organized for incremental improvements with clear separation of concerns.

**Contributing Areas**:
- Parser improvements (move to AST-based)
- New gap detectors
- Test framework support
- Report generation

---

## 📄 License

MIT

---

## 🎯 Vision

Move from "Did we test enough?" to "Did we test the right things?"
