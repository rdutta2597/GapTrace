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

### Option 1: Dev Container (Recommended for VS Code)

```bash
# Clone the repository
git clone <repo-url>
cd GapTrace

# Open in VS Code
code .

# When prompted, click "Reopen in Container"
# Or from command palette: Dev Containers: Reopen in Container
```

The dev container automatically:
- ✅ Installs all dependencies
- ✅ Sets up libclang for AST parsing
- ✅ Creates Python virtual environment
- ✅ Installs dev tools (pytest, black, ruff)

### Option 2: Local Installation

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

**macOS:** Install LLVM first:
```bash
brew install llvm
export LLVM_CONFIG_PATH=$(brew --prefix llvm)
```

### Option 3: Docker Compose

```bash
# Clone the repository
git clone <repo-url>
cd GapTrace

# Build and run dev container
docker-compose -f docker-compose.dev.yml run dev
```

### Current Usage (v0.1.0)

```bash
# ✅ RECOMMENDED: Parse C++ file with AST-based analysis (Phase 1)
gaptrace parse --src src/main.cpp

# Parse with coverage mapping
gaptrace parse --src src/main.cpp --coverage lcov.info

# Export to JSON
gaptrace parse --src src/main.cpp --output results.json

# ✅ NEW (Phase 2): Analyze gaps with scenario descriptions (mock LLM)
gaptrace analyze --src src/main.cpp --coverage lcov.info

# Analyze with OpenAI (requires OPENAI_API_KEY)
gaptrace analyze --src src/main.cpp --coverage lcov.info --openai

# Export analysis results
gaptrace analyze --src src/main.cpp --coverage lcov.info --output report.json

# View help
gaptrace --help
gaptrace parse --help
gaptrace analyze --help

# Legacy: Scan for basic file info (heuristic-based, not recommended)
gaptrace scan ./gaptrace/sample_project
```

### Example Output (v0.1.0)

Parse command output:
```
✅ Parsed gaptrace/sample_project/example.cpp

📊 Analysis Results
  Functions: 4
  Decision Points: 8
  Coverage: 37.5%

⚠️  Critical Gaps (uncovered critical paths):
  getStatus():
    - Line 19: switch
  calculateDiscount():
    - Line 49: if
    - Line 51: if
    - Line 53: if
```

---

## 📋 Current Features (v0.2.0 - Phase 1-2)

### ✅ What Works Now (Phase 1 + Phase 2)
- **AST Parser**: libclang-based C/C++ parsing with decision point extraction ✅
- **Coverage Reader**: LCOV .info file parsing and integration ✅
- **Parse Command**: `gaptrace parse --src <file> --coverage <file> --output <file>` ✅
- **Gap Analyzer**: Identifies uncovered logical paths in code ✅ (Phase 2)
- **LLM Integration**: Abstract LLM interface with mock + OpenAI support ✅ (Phase 2)
- **Analyze Command**: `gaptrace analyze --src <file> --coverage <file> [--openai]` ✅ (Phase 2)
- **JSON Export**: Complete results exported to JSON ✅
- **File Discovery**: Finds C/C++ files (`.cpp`, `.cc`, `.cxx`, `.c`, `.h`, `.hpp`, `.hxx`)

### 🏗️ Current Project Structure
```
gaptrace/
├── __init__.py           # Package initialization
├── cli.py                # CLI with parse & analyze commands ✅
├── scanner.py            # File discovery (works)
├── function_parser.py    # Function extraction (works)
├── test_parser.py        # Test pattern detection (basic)
├── gap_detector.py       # Gap detection (heuristic-based)
├── models/               # Data models — PHASE 1 ✅
│   ├── __init__.py
│   └── decision_point.py # DecisionPoint, Coverage, FunctionAnalysis
├── parser/               # AST parsing — PHASE 1 ✅
│   ├── __init__.py
│   └── ast_parser.py     # libclang-based C++ AST parser (WORKING)
├── coverage/             # Coverage file parsing — PHASE 1 ✅
│   ├── __init__.py
│   └── lcov_reader.py    # LCOV .info file parser
├── analyzer/             # Gap analyzer — PHASE 2 ✅
│   ├── __init__.py
│   └── gap_analyzer.py   # Core gap detection logic (WORKING)
├── llm/                  # LLM integration — PHASE 2 ✅
│   ├── __init__.py
│   ├── base_client.py    # Abstract LLM interface
│   ├── mock_client.py    # Mock client (no API needed)
│   └── openai_client.py  # OpenAI GPT-4o client (optional)
└── sample_project/       # Example files
    ├── math.cpp
    ├── math_test.cpp
    ├── example.cpp       # Complex example with 61 functions, 15 decision points
    └── example.info      # Sample lcov coverage file
```

### ⚠️ Current Limitations (Phase 3+ Work)
- **Scenario Mapping** — Basic descriptions, no test-to-code mapping yet (Phase 3)
- **Report Formatting** — CLI output only, no markdown reports yet (Phase 3)

---

## 📦 Phase 1-2: ✅ COMPLETE

**Phase 1 Deliverables:**
- ✅ Data Models: DecisionPoint, Coverage, FunctionAnalysis, ParseResult
- ✅ AST Parser: libclang-based C/C++ parser with decision point detection  
- ✅ Coverage Reader: LCOV .info file integration
- ✅ CLI Integration: `gaptrace parse --src <file> --coverage <file> --output <file>`

**Phase 2 Deliverables:**
- ✅ Gap Analyzer: Identifies uncovered logical paths
- ✅ LLM Interface: Abstract design with MockClient + OpenAIClient
- ✅ Analyze Command: `gaptrace analyze --src <file> --coverage <file>`
- ✅ Scenario Descriptions: Mock templates (ready for OpenAI integration)
- ✅ JSON Export: Gap analysis results

**Ready for Phase 3: Report Formatting & CLI Polish**

---

## 📊 Phase 1-2 Status Bar

```
[████████████████████████████████████████████████] 100% COMPLETE ✅
```

---

## 🏗️ Architecture (GapTrace Vision)

### Phase 1-5: End-to-End Flow

```
Your C++ source file
        ↓
  [Clang AST Parser]        ← extracts functions, branches, conditions ✅
        ↓
  [gcov/lcov Parser]        ← reads coverage report, maps to AST ✅
        ↓
  [Gap Analyzer]            ← finds branches that ARE covered but
        ↓                      scenarios that are logically missing (Phase 2)
  [LLM Engine]              ← sends context to OpenAI, gets
        ↓                      missing scenario descriptions (Phase 2)
  [Report Generator]        ← outputs to terminal or markdown file (Phase 3)
```

### Project Structure (Phase 1 Complete)

```
gaptrace/
├── cli.py                 # CLI with parse command ✅
├── scanner.py             # File discovery (foundation)
├── models/                # Data models ✅
│   ├── __init__.py
│   └── decision_point.py  # DecisionPoint, Coverage, etc.
├── parser/                # AST parsing ✅
│   ├── __init__.py
│   └── ast_parser.py      # libclang parser
├── coverage/              # Coverage reader ✅
│   ├── __init__.py
│   └── lcov_reader.py     # LCOV file parser
├── analyzer/              # Gap analyzer (Phase 2)
├── llm/                   # LLM integration (Phase 2)
├── output/                # Report formatting (Phase 3)
└── sample_project/        # Example C++ project
```

---

## 🤖 Using the LLM Integration

### Option 1: Mock LLM (Default - No API Key Needed)
```bash
# Use built-in mock client for testing
gaptrace analyze --src src/main.cpp --coverage lcov.info
```

This uses pre-defined scenario templates without requiring any API key. Perfect for development!

### Option 2: OpenAI GPT-4o (Real Descriptions)
```bash
# 1. Get API key from https://platform.openai.com/api-keys
# 2. Set environment variable
export OPENAI_API_KEY="sk-..."

# 3. Run with --openai flag
gaptrace analyze --src src/main.cpp --coverage lcov.info --openai
```

**Cost**: ~$0.005-0.01 per file analyzed (depends on file size)

### Option 3: Bring Your Own LLM
You can implement a custom LLM client:
```python
from gaptrace.llm import LLMClient

class CustomLLMClient(LLMClient):
    def describe_gap(self, function_name, decision_type, line_number, source_code):
        # Your implementation here
        return "Custom gap description..."

analyzer = GapAnalyzer(llm_client=CustomLLMClient())
```

---

Once Phases 1-2 are complete, users will see:

```
$ gaptrace analyze --src network_handler.cpp --coverage lcov.info

GapTrace v1.0 — Scenario Gap Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 network_handler.cpp

  ┌─ connect() — 3 gaps found
  │
  │  ⚠ MISSING: connection timeout scenario
  │    → All tests call connect() with responsive servers.
  │      No test exercises behavior when server takes >30s to respond.
  │
  │  ⚠ MISSING: simultaneous connection attempts
  │    → connect() has a mutex guard but no test verifies
  │      thread-safety under concurrent calls.
  │
  │  ⚠ MISSING: invalid port range (0 or >65535)
  │    → Port validation branch is covered but only with
  │      valid ports. Boundary values never tested.

Coverage: 87% ✅  |  Logical gaps: 3 ⚠  |  Risk: MEDIUM
```

**⚠️ Currently (v0.1.0)**: Use `gaptrace scan` with heuristic-based output. Full analysis coming Phase 1-2.

---

## 🛠️ Tech Stack

| Layer | Technology | Details |
|-------|-----------|----------|
| **Language** | Python 3.11+ | |
| **AST Parsing** | libclang (Python bindings) | `clang` pip package |
| **Coverage** | lcov .info files | gtest + gcov native output |
| **LLM** | OpenAI gpt-4o | via `openai` SDK |
| **CLI** | Typer | Type-safe commands |
| **Output** | Rich + Markdown | Terminal formatting + file reports |
| **Packaging** | pyproject.toml | `pip install gaptrace` |

### Dependencies (to be added Phase 1)
```toml
dependencies = [
    "typer",           # CLI framework
    "rich",            # Terminal formatting
    "clang",           # AST parsing
    "openai",          # LLM integration
]
```

---

## 📅 Build Phases (Phases 1-5)

### Phase 1 — Parser + Coverage Reader
**Goal**: Outputs raw JSON of decision points
- [x] Implement libclang AST parser
- [x] Build lcov/gcov coverage file reader
- [x] Extract decision points (branches, conditions, loops)
- [x] JSON output working

### Phase 2 — Gap Analyzer + LLM Integration
**Goal**: Gap analyzer logic working, LLM returns scenario descriptions
- [x] Implement gap analyzer (coverage → AST mapping)
- [x] Integrate LLM interface (abstract + mock + OpenAI)
- [x] Basic terminal output formatting
- [x] Test end-to-end on sample project
- [ ] Refine gap detection heuristics
- [ ] Add more scenario templates

### Phase 3 — CLI Polish + Markdown Reports
**Goal**: Production-ready CLI with multiple output formats
- [ ] Error handling and validation
- [ ] Add `gaptrace analyze --src foo.cpp --coverage lcov.info`
- [ ] Add `--out markdown` flag for reports
- [ ] Add `--json` and `--verbose` flags
- [ ] Polish help text and examples

### Phase 4 — Real-World Testing + PyPI Release
**Goal**: Tested on real repos, published to PyPI
- [ ] Test on 2-3 open-source C++ repositories
- [ ] Fix edge cases and performance issues
- [ ] Create installation guide
- [ ] Publish to PyPI

### Phase 5 — VS Code Extension
**Goal**: IDE integration for seamless gap analysis
- [ ] Build VS Code extension in TypeScript
- [ ] Integrate with CLI backend
- [ ] Real-time gap detection in editor
- [ ] Publish to VS Code marketplace

---

## ⚠️ Current Status

**v0.2.0 (Current - Phase 1-2)**
- ✅ CLI foundation with subcommands (`parse`, `analyze`, `scan`)
- ✅ File discovery and classification
- ✅ Function extraction (AST-based)
- ✅ AST parser with decision point extraction (Phase 1)
- ✅ Coverage reader (Phase 1)
- ✅ Gap analyzer (Phase 2)
- ✅ LLM interface with mock + OpenAI support (Phase 2)
- ❌ Markdown reports (coming Phase 3)
- ❌ VS Code extension (coming Phase 5)

**What v0.2.0 Does**: 
- Parse C++ with AST, extract decision points
- Read LCOV coverage files
- Analyze gaps with mock scenario descriptions
- Ready to integrate OpenAI for real LLM descriptions

**What v0.2.0 Doesn't Do**: 
- Real markdown report generation (Phase 3)
- Test-to-code mapping (Phase 3)
- VS Code extension (Phase 5)

---

## 📝 Development Roadmap

This is an active development project with a 5-phase roadmap:

**Phase 1**: AST parser + coverage reader (JSON output)
**Phase 2**: Gap analyzer + LLM integration (scenario descriptions)
**Phase 3**: CLI polish + markdown reports (production-ready)
**Phase 4**: Real-world testing + PyPI release (available for install)
**Phase 5**: VS Code extension (IDE integration)

---

## 📄 License

MIT

---

## 🎯 Vision

Move from "Did we test enough?" to "Did we test the right things?"
