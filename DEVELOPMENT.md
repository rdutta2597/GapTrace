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
# Parse a C++ file with AST analysis
gaptrace parse --src example.cpp

# Parse with coverage mapping
gaptrace parse --src example.cpp --coverage lcov.info

# Export results to JSON
gaptrace parse --src example.cpp --output results.json

# Show CLI help
gaptrace --help
gaptrace parse --help
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

# Lint with Ruff
ruff check gaptrace/

# Type checking (if enabled)
pylint gaptrace/
```

## Project Structure

```
GapTrace/
├── gaptrace/                   # Main package
│   ├── cli.py                  # CLI commands (scan, parse, version)
│   ├── scanner.py              # File discovery and classification
│   ├── models/                 # Data models
│   │   └── decision_point.py  # DecisionPoint, Coverage, etc.
│   ├── parser/                 # AST parsing
│   │   └── ast_parser.py       # libclang-based parser
│   ├── coverage/               # Coverage file readers
│   │   └── lcov_reader.py      # LCOV .info parser
│   ├── sample_project/         # Example C++ code
│   │   ├── example.cpp
│   │   └── example.info
│   └── (legacy files)
│       ├── function_parser.py
│       ├── test_parser.py
│       └── gap_detector.py
├── .devcontainer/              # Dev container configuration
│   ├── devcontainer.json
│   ├── Dockerfile
│   └── post-create.sh
├── tests/                      # Unit tests (to be added)
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # This file
└── .gitignore                  # Git ignore rules
```

## Key Components

### Data Models (`gaptrace/models/decision_point.py`)
- `DecisionType`: Enum of decision point types (if, switch, loop, etc.)
- `Coverage`: Line and branch coverage tracking
- `DecisionPoint`: A decision point in code with coverage info
- `FunctionAnalysis`: Per-function analysis with decision points
- `ParseResult`: Complete file analysis result

### AST Parser (`gaptrace/parser/ast_parser.py`)
- Uses libclang to parse C/C++ files
- Extracts functions and decision points
- Identifies critical paths (null checks, error returns)
- Exports results to JSON

### Coverage Reader (`gaptrace/coverage/lcov_reader.py`)
- Parses LCOV `.info` files from gcov/gtest
- Maps coverage data to decision points
- Updates parse results with coverage information

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

4. Commit with clear messages:
   ```bash
   git commit -m "Add: description of changes"
   ```

5. Push and create a pull request

## Phase Roadmap

- **Phase 1** ✅ COMPLETE: AST Parser + Coverage Reader
- **Phase 2** 🔄 TODO: Gap Analyzer + LLM Integration
- **Phase 3** 🔄 TODO: CLI Polish + Markdown Reports
- **Phase 4** 🔄 TODO: Real-World Testing + PyPI Release
- **Phase 5** 🔄 TODO: VS Code Extension

## Troubleshooting

### libclang not found
- macOS: `export LLVM_CONFIG_PATH=$(brew --prefix llvm)`
- Linux: Install `libclang-11-dev` package

### Python version issues
- Requires Python 3.11+
- Check with: `python --version`

### Dev container won't open
- Ensure Docker Desktop is running
- Try: Dev Containers: Rebuild Container
- Check Docker logs: `docker logs -f gaptrace-dev`

## Resources

- [libclang Documentation](https://clang.llvm.org/doxygen/index.html)
- [Typer CLI Framework](https://typer.tiangolo.com/)
- [LCOV Format](http://ltp.sourceforge.net/coverage/lcov.php)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
