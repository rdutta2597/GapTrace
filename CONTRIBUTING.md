# Contributing to GapTrace

Thank you for your interest in contributing! GapTrace is a developer-first CLI tool that detects missing unit test scenarios in C/C++ codebases using LLM-powered analysis.

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
pip install -e ".[dev]"
```

Make sure you have `clang` and `lcov` installed:

```bash
# Ubuntu/Debian
sudo apt-get install clang libclang-dev lcov

# macOS
brew install llvm lcov
```

### 4. Make Your Changes

- Keep changes focused — one PR per feature or fix
- Follow existing code style (PEP 8 for Python)
- Add or update tests for your changes
- Update documentation if behavior changes

### 5. Test Your Changes

```bash
pytest tests/
```

Please ensure all tests pass before opening a PR.

### 6. Open a Pull Request

- Target branch: `main`
- Fill in the PR template completely
- Link the related issue (e.g., `Closes #42`)
- Keep your PR description clear — what changed and why

---

## What We Welcome

- Bug fixes
- Performance improvements to the AST parser or coverage mapper
- Support for additional C++ test frameworks (Catch2, Boost.Test)
- Improved LLM prompting strategies
- Better output formatting
- Documentation improvements
- Example C++ codebases for testing

## What to Avoid

- Unrelated changes bundled into one PR
- Breaking changes to the CLI interface without prior discussion
- Adding new dependencies without opening an issue first

---

## Code Style

- Python 3.11+
- Follow PEP 8
- Use type hints where possible
- Keep functions small and focused
- Write docstrings for public functions

---

## Reporting Bugs

Open an issue with:
- Your OS and Python version
- The command you ran
- The full error output
- A minimal reproducible example if possible

---

## Questions?

Open a [GitHub Discussion](../../discussions) — not an issue — for general questions or ideas.

---

## License

By contributing, you agree that your contributions will be licensed under the same license as this project.
