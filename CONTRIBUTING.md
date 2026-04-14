# Contributing to GapTrace

Thank you for your interest in contributing! GapTrace is a developer-first CLI tool that detects missing unit test scenarios in C/C++ codebases by analyzing source code structure and comparing it against coverage reports, then using LLM to explain what test scenarios are missing.

---

## Before You Start

Please **open an issue before writing any code.** This avoids duplicate work and ensures your contribution aligns with the project direction. For small fixes (typos, docs), you can skip this step.

---

## How to Contribute

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/gaptrace.git
cd gaptrace
```

### 2. Create a Branch

Always branch off `main`. Use a descriptive name:

```bash
git checkout -b feat/add-catch2-support
git checkout -b fix/lcov-parser-edge-case
git checkout -b docs/improve-readme
```

Branch naming conventions:
- `feat/` — new feature
- `fix/` — bug fix
- `docs/` — documentation only
- `refactor/` — code restructure, no behavior change
- `test/` — adding or improving tests

### 3. Set Up Locally

```bash
# Install in development mode
pip install -e .

# Optional: Install dev dependencies if available
pip install black ruff pytest
```

Make sure you have `clang` and `lcov` installed:

```bash
# Ubuntu/Debian (Dev Container)
# Already installed in dev container - no action needed

# Ubuntu/Debian (Local)
sudo apt-get install clang-11 libclang-11-dev lcov

# macOS
brew install llvm lcov
export LLVM_CONFIG_PATH=$(brew --prefix llvm)
```

### 4. Make Your Changes

- Keep changes focused — one PR per feature or fix
- Follow existing code style (PEP 8 for Python)
- Add or update tests for your changes
- Update documentation if behavior changes
- Test both mock and OpenAI LLM modes

### 5. Test Your Changes

```bash
# Run all tests
pytest tests/

# Test CLI commands
gaptrace parse --src gaptrace/sample_project/example.cpp
gaptrace analyze --src gaptrace/sample_project/example.cpp --coverage gaptrace/sample_project/example.info

# Test with OpenAI (optional, requires API key)
export OPENAI_API_KEY="your-key-here"
gaptrace analyze --src gaptrace/sample_project/example.cpp --coverage gaptrace/sample_project/example.info --openai
```

Please ensure all tests pass before opening a PR.

### 6. Open a Pull Request

- Target branch: `main`
- Fill in the PR template completely
- Link the related issue (e.g., `Closes #42`)
- Keep your PR description clear — what changed and why

---

## What We Welcome

- Bug fixes and performance improvements
- Support for additional C++ test frameworks (Catch2, Boost.Test, Google Test)
- Enhanced LLM prompting strategies and scenario templates
- New LLM provider integrations (Claude, Gemini, local models)
- Better output formatting and CLI UX improvements
- Additional coverage format support (beyond LCOV)
- Documentation improvements and examples
- Test case contributions for edge cases

### Current Development Focus (Phase 3)

Since Phase 1-2 are complete, we're focusing on:
- **CLI Polish**: Better error messages, progress indicators, help text
- **Report Generation**: Markdown/HTML report formats
- **Test-to-Code Mapping**: Linking test files to source code gaps
- **Real-world Testing**: Validating on open-source C++ projects

## What to Avoid

- Unrelated changes bundled into one PR
- Breaking changes to the CLI interface without prior discussion
- Adding new dependencies without opening an issue first
- Large architectural changes without design discussion

---

## Code Style

- Python 3.11+
- Follow PEP 8
- Use type hints where possible
- Keep functions small and focused
- Write docstrings for public functions
- Use `black` for formatting and `ruff` for linting

---

## Testing Guidelines

- Add unit tests for new functionality
- Test both mock and OpenAI LLM modes
- Include integration tests for CLI commands
- Test with the sample project: `gaptrace/sample_project/example.cpp`
- Ensure tests work in both dev container and local environments

---

## Reporting Bugs

Open an issue with:
- Your OS and Python version
- The command you ran
- The full error output
- A minimal reproducible example if possible
- Whether you're using dev container or local setup

---

## Questions?

Open a [GitHub Discussion](../../discussions) — not an issue — for general questions or ideas.

---

## License

By contributing, you agree that your contributions will be licensed under the same license as this project.
