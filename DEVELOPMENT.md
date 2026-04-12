# Development Guide

## Setting Up Your Development Environment

### With Dev Container (Recommended)

1. Install VS Code extensions:
   - Remote - Containers (ms-vscode-remote.remote-containers)
   - Dev Containers (ms-vscode.remote-container-wsl)

2. Open the project in VS Code:
   ```bash
   code .
   ```

3. When prompted, click "Reopen in Container" or:
   - Press `Cmd/Ctrl + Shift + P`
   - Search for "Dev Containers: Reopen in Container"

4. Wait for the container to build and environment to be set up

5. You're ready to develop!

### With Local Installation

1. Install LLVM (required for libclang):
   ```bash
   # macOS
   brew install llvm
   export LLVM_CONFIG_PATH=$(brew --prefix llvm)
   
   # Ubuntu/Debian
   sudo apt-get install llvm-11-dev libclang-11-dev
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. Install project in development mode:
   ```bash
   pip install -e .
   ```

## Development Workflow

### Running Commands

```bash
# Parse a C++ file with AST analysis (Phase 1)
gaptrace parse --src example.cpp

# Parse with coverage mapping
gaptrace parse --src example.cpp --coverage lcov.info

# Export parse results to JSON
gaptrace parse --src example.cpp --output results.json

# Analyze gaps with LLM descriptions (Phase 2 - Mock LLM)
gaptrace analyze --src example.cpp --coverage lcov.info

# Analyze with OpenAI GPT-4o (requires OPENAI_API_KEY)
export OPENAI_API_KEY="sk-..."
gaptrace analyze --src example.cpp --coverage lcov.info --openai

# Export analysis results to JSON
gaptrace analyze --src example.cpp --coverage lcov.info --output report.json

# Show CLI help
gaptrace --help
gaptrace parse --help
gaptrace analyze --help
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gaptrace

# Run specific test file
pytest tests/test_parser.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with Black
black gaptrace/

# Lint with Ruff (fast, comprehensive)
ruff check gaptrace/

# Fix auto-fixable issues
ruff check --fix gaptrace/

# Type checking with mypy (if configured)
mypy gaptrace/
```

**Code Quality Tools:**
- **Black**: Code formatting (PEP 8 compliant)
- **Ruff**: Fast Python linter (replaces flake8, isort, pylint for speed)
- **MyPy**: Type checking (optional, for strict type safety)

## Project Structure

```
GapTrace/
├── gaptrace/                   # Main package
│   ├── cli.py                  # CLI commands (parse, analyze)
│   ├── scanner.py              # File discovery and classification
│   ├── models/                 # Data models (Phase 1)
│   │   └── decision_point.py   # DecisionPoint, Coverage, FunctionAnalysis
│   ├── parser/                 # AST parsing (Phase 1)
│   │   └── ast_parser.py       # libclang-based C++ AST parser
│   ├── coverage/               # Coverage file readers (Phase 1)
│   │   └── lcov_reader.py      # LCOV .info file parser
│   ├── analyzer/               # Gap analyzer (Phase 2)
│   │   └── gap_analyzer.py     # Core gap detection logic
│   ├── llm/                    # LLM integration (Phase 2)
│   │   ├── __init__.py
│   │   ├── base_client.py      # Abstract LLMClient interface
│   │   ├── mock_client.py      # Mock client (no API needed)
│   │   └── openai_client.py    # OpenAI GPT-4o client
│   ├── sample_project/         # Example C++ code and coverage
│   │   ├── example.cpp         # Complex example (61 functions)
│   │   ├── example.info        # LCOV coverage data
│   │   ├── math.cpp            # Simple math functions
│   │   └── math_test.cpp       # Test file
│   └── (legacy files)
│       ├── function_parser.py  # Legacy heuristic parser
│       ├── test_parser.py      # Legacy test pattern detection
│       └── gap_detector.py     # Legacy gap detection
├── docs/                       # Documentation
│   └── gaptrace_arch.md        # Architecture documentation
├── tests/                      # Unit tests (to be expanded)
├── .devcontainer/              # Dev container configuration
│   ├── devcontainer.json
│   ├── Dockerfile
│   └── post-create.sh          # Automated setup script
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # Main project README
├── DEVELOPMENT.md              # This development guide
├── CONTRIBUTING.md             # Contributing guidelines
├── INTERVIEW_README.md         # Interview preparation master guide
├── INTERVIEW_QUICK_REFERENCE.md # 5-min interview cheat sheet
├── INTERVIEW_GUIDE.md          # 20-min deep dive guide
├── INTERVIEW_CODE_WALKTHROUGH.md # Live demo reference
├── SUMMARY.txt                 # Project summary
└── .gitignore                  # Git ignore rules
```

## Key Components

### Data Models (`gaptrace/models/decision_point.py`)
- `DecisionPoint`: A decision point in code (if/switch/loop/call) with line number and source
- `FunctionAnalysis`: Per-function analysis containing decision points
- `ParseResult`: Complete file analysis result with all functions
- `CoverageData`: Coverage information mapped to lines
- `Gap`: Represents a missing test scenario with severity and description

### AST Parser (`gaptrace/parser/ast_parser.py`)
- Uses libclang 11.0 to parse C/C++ files into AST
- Extracts functions and decision points (if, switch, loops, function calls)
- Identifies critical paths and business logic
- Exports structured results for gap analysis

### Coverage Reader (`gaptrace/coverage/lcov_reader.py`)
- Parses LCOV `.info` files from gcov/lcov tools
- Maps line execution counts to decision points
- Calculates coverage statistics
- Integrates coverage data with AST analysis

### Gap Analyzer (`gaptrace/analyzer/gap_analyzer.py`) - Phase 2
- Compares parse results with coverage data
- Identifies uncovered decision points
- Calculates severity scores (critical/high/medium/low)
- Prepares gaps for LLM description

### LLM Integration (`gaptrace/llm/`) - Phase 2
- **Abstract Base**: `base_client.py` - Defines LLMClient interface
- **Mock Client**: `mock_client.py` - Template-based descriptions (no API needed)
- **OpenAI Client**: `openai_client.py` - GPT-4o integration (optional API key)
- Supports dependency injection for different LLM providers

### CLI (`gaptrace/cli.py`)
- `parse` command: AST parsing with optional coverage mapping
- `analyze` command: Full gap analysis with LLM descriptions
- Rich terminal output with tables and formatting
- JSON export support
- Optional OpenAI integration

## Contributing

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and test:
   ```bash
   pytest
   gaptrace parse --src test_file.cpp
   ```

3. Format and lint:
   ```bash
   black gaptrace/
   ruff check gaptrace/
   ```

4. Test both LLM modes:
   ```bash
   # Test mock LLM (no API key needed)
   gaptrace analyze --src gaptrace/sample_project/example.cpp --coverage gaptrace/sample_project/example.info
   
   # Test OpenAI LLM (requires API key)
   export OPENAI_API_KEY="your-key-here"
   gaptrace analyze --src gaptrace/sample_project/example.cpp --coverage gaptrace/sample_project/example.info --openai
   ```

5. Commit with clear messages:
   ```bash
   git commit -m "feat: add new LLM provider support
   
   - Add ClaudeClient implementation
   - Update CLI to support --claude flag
   - Add tests for new provider"
   ```

6. Push and create a pull request

## Phase Roadmap

- **Phase 1** ✅ COMPLETE: AST Parser + Coverage Reader (v0.1.0)
- **Phase 2** ✅ COMPLETE: Gap Analyzer + LLM Integration (v0.2.0)
- **Phase 3** 🔄 CURRENT: CLI Polish + Markdown Reports
- **Phase 4** 🔄 TODO: Real-World Testing + PyPI Release
- **Phase 5** 🔄 TODO: VS Code Extension

### Current Status (v0.2.0)
- ✅ Full E2E pipeline: Parse → Coverage → Analyze → Describe
- ✅ Abstract LLM interface with mock + OpenAI implementations
- ✅ CLI with `parse` and `analyze` commands
- ✅ JSON export and Rich terminal formatting
- ✅ Dev container setup with automated LLVM/Clang installation
- ✅ Comprehensive documentation and interview materials

## Troubleshooting

### libclang not found
- **Dev Container**: Already configured in `post-create.sh`
- **macOS**: `export LLVM_CONFIG_PATH=$(brew --prefix llvm)`
- **Linux**: Install `libclang-11-dev` package (version 11 required, pinned in pyproject.toml)

### Python version issues
- Requires Python 3.11+
- Check with: `python --version`
- Dev container uses Python 3.11

### OpenAI API issues
- Set environment variable: `export OPENAI_API_KEY="sk-..."`
- Use mock client for development: omit `--openai` flag
- Check API key validity if getting auth errors

### Dev container won't open
- Ensure Docker Desktop is running
- Try: Dev Containers: Rebuild Container
- Check Docker logs: `docker logs -f gaptrace-dev`
- Verify VS Code extensions are installed

### Import errors
- Activate virtual environment: `source .venv/bin/activate`
- Install dependencies: `pip install -e .`
- Check Python path includes project root

### AST parsing fails
- Verify C++ file is valid and compilable
- Check libclang version: `python -c "import clang; print(clang.__version__)"`
- Ensure LLVM 11 is installed (not newer versions)

## Interview Preparation

The project includes comprehensive interview materials:

- **INTERVIEW_README.md**: Master guide for all interview prep materials
- **INTERVIEW_QUICK_REFERENCE.md**: 5-minute cheat sheet
- **INTERVIEW_GUIDE.md**: 20-minute deep dive with examples
- **INTERVIEW_CODE_WALKTHROUGH.md**: Live demo reference with 7 code examples
- **SUMMARY.txt**: Quick project overview

Use these for technical interviews or project presentations.

## Resources

- [libclang Documentation](https://clang.llvm.org/doxygen/index.html)
- [Typer CLI Framework](https://typer.tiangolo.com/)
- [Rich Terminal UI](https://rich.readthedocs.io/)
- [OpenAI API](https://platform.openai.com/docs)
- [LCOV Format](http://ltp.sourceforge.net/coverage/lcov.php)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Ruff Linter](https://beta.ruff.rs/docs/)

### Architecture Documentation

- `docs/gaptrace_arch.md`: Complete architecture overview
- `INTERVIEW_GUIDE.md`: Deep dive with examples
- `INTERVIEW_CODE_WALKTHROUGH.md`: Code walkthrough demos
