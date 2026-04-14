# GapTrace Architecture & Flow Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Overview](#component-overview)
4. [Data Flow](#data-flow)
5. [Detailed Component Descriptions](#detailed-component-descriptions)
6. [Design Patterns](#design-patterns)
7. [Module Dependencies](#module-dependencies)
8. [Example Walkthrough](#example-walkthrough)

---

## Project Overview

**GapTrace** is a CLI tool that identifies missing unit test scenarios in C++ codebases by:
1. Parsing source code structure (decision points: if/switch/loops/calls)
2. Mapping coverage data from LCOV reports
3. Analyzing which decision points are untested
4. Using LLM to explain what test scenarios are missing

**Core Problem Solved:**
Code coverage metrics (line coverage %) don't reveal missing important test scenarios. A function can have 100% line coverage but only test the happy path, missing critical edge cases.

**Solution Approach:**
GapTrace identifies logically important code branches that aren't covered by tests and generates natural language descriptions of what scenarios should be tested.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI LAYER (cli.py)                      │
│  Commands: parse, analyze                                       │
│  User Interface: Typer + Rich formatting                        │
└────────────────────┬──────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│  Phase 1: PARSE  │      │ Phase 1: COVERAGE│
│  (ast_parser)    │      │ (lcov_reader)    │
├──────────────────┤      ├──────────────────┤
│ Input: .cpp file │      │ Input: .info     │
│ Output: ParseRes │      │ Output: Coverage │
│                  │      │                  │
│ Uses: libclang   │      │ Parses: LCOV fmt │
│ AST             │      │ Maps: line data  │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  Phase 2: ANALYZE           │
        │  (gap_analyzer.py)          │
        ├─────────────────────────────┤
        │ Input: ParseResult + Cov    │
        │ Action: Find gaps, calc     │
        │         severity            │
        │ Output: Gap[] objects       │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │  Phase 2: DESCRIBE          │
        │  (llm/base_client)          │
        ├─────────────────────────────┤
        │ Uses: LLMClient interface   │
        │ Impl: MockClient (default)  │
        │       OpenAIClient (opt)    │
        │ Output: Gap descriptions    │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │  OUTPUT FORMATTING          │
        │  Rich terminal display      │
        │  JSON export (optional)     │
        └─────────────────────────────┘
```

---

## Component Overview

### Layer 1: Interface Layer

**CLI (`gaptrace/cli.py`)**
- **Purpose**: User-facing command-line interface
- **Framework**: Typer + Rich
- **Commands**:
  - `gaptrace parse --src FILE` - Extract functions and decision points
  - `gaptrace analyze --src FILE --coverage FILE [--openai] [--output FILE]` - Full analysis
- **Responsibilities**:
  - Parse command-line arguments
  - Orchestrate phase execution
  - Format output (table/JSON)
  - Handle errors gracefully

---

### Layer 2: Processing Layers

#### Phase 1A: Parser

**Component**: `gaptrace/parser/ast_parser.py`

**Purpose**: Extract code structure from C++ source files

**How It Works**:
1. Uses `libclang` (Python bindings to LLVM/Clang)
2. Parses C++ code into Abstract Syntax Tree (AST)
3. Walks AST to find:
   - Functions (declarations and definitions)
   - Decision points: if statements, switch statements, loops, function calls
4. Creates structured data: `DecisionPoint`, `FunctionAnalysis`, `ParseResult`

**Key Methods**:
- `parse_file(filename: str) -> ParseResult`: Main entry point
- `_extract_functions()`: Find all functions in file
- `_extract_decision_points()`: Find all decision points in function
- `_is_decision_point()`: Classify cursor as decision point

**Output**: `ParseResult` containing:
```python
ParseResult(
    functions=[FunctionAnalysis(...), ...],
    file_path="...",
    language="C++"
)
```

**Why AST instead of Regex?**
- Regex can't understand C++ syntax (nested braces, macros, templates)
- AST provides semantic understanding
- Correctly handles comments, strings, preprocessor directives
- Identifies actual control flow, not just patterns

---

#### Phase 1B: Coverage Reader

**Component**: `gaptrace/coverage/lcov_reader.py`

**Purpose**: Parse LCOV coverage files and map to code lines

**How It Works**:
1. Reads `.info` files (LCOV format from `gcov`)
2. Extracts line execution counts
3. Maps coverage data to `DecisionPoint` objects:
   - Line number → execution count (0 = uncovered, >0 = covered)
4. Creates `CoverageData` object

**LCOV Format Structure**:
```
TN:<total lines>
LH:<covered lines>
DA:<line>,<count>
DA:<line>,<count>
end_record
```

**Key Methods**:
- `read_coverage(filepath: str) -> CoverageData`: Main entry point
- `_parse_line_data()`: Extract line coverage from DA records
- `_calculate_statistics()`: Compute coverage percentages

**Output**: `CoverageData` containing:
```python
CoverageData(
    line_coverage={
        line_num: execution_count,  # e.g., {42: 0, 43: 5, ...}
        ...
    },
    stats=CoverageStats(...)
)
```

---

#### Phase 2A: Gap Analyzer

**Component**: `gaptrace/analyzer/gap_analyzer.py`

**Purpose**: Identify uncovered decision points and rate their importance

**How It Works**:
1. Takes `ParseResult` and `CoverageData`
2. For each function, iterates through decision points
3. Checks if decision point is covered (execution count > 0)
4. For uncovered decisions, calculates severity:
   - **Critical**: Decisions marked as business-critical
   - **High**: Loops, complex conditions
   - **Medium**: Simple if statements
   - **Low**: Utility functions, rarely-executed paths
5. Creates `Gap` objects for each missing scenario

**Key Methods**:
- `analyze(parse_result, coverage) -> List[Gap]`: Main entry point
- `_find_uncovered_decisions()`: Find unexecuted branches
- `_calculate_severity()`: Score importance (critical/high/medium/low)
- `_is_critical()`: Heuristic to identify business-critical code

**Severity Calculation**:
```python
def _calculate_severity(decision_type, is_critical, has_loops):
    if is_critical:
        return "critical"
    elif decision_type in ("loop", "switch"):
        return "high"
    elif decision_type == "if":
        return "medium"
    else:
        return "low"
```

**Output**: `Gap[]` containing:
```python
Gap(
    function_name="validatePayment",
    decision_type="if",  # What kind of decision
    line_number=42,
    severity="high",
    source_code="if (amount <= 0)",
    description=None  # Filled by LLM later
)
```

---

#### Phase 2B: LLM Integration

**Base Interface**: `gaptrace/llm/base_client.py`

**Purpose**: Abstract interface for LLM implementations (dependency inversion)

**Interface**:
```python
class LLMClient(ABC):
    @abstractmethod
    def describe_gap(self, 
                    function_name: str,
                    decision_type: str,
                    line_number: int,
                    source_code: str) -> str:
        """Generate natural language description of test gap"""
        pass
```

**Why Abstract?**
- Decouples analyzer from specific LLM
- Easy to swap implementations (mock ↔ real API)
- Enables testing without API keys
- Can add new LLM providers later

---

**Implementation 1: MockLLMClient** (`gaptrace/llm/mock_client.py`)

**Purpose**: Template-based LLM for development/testing (no API calls)

**How It Works**:
1. Uses pre-written templates based on decision type
2. Maps decision type → relevant scenarios:
   - `if`: Condition true, condition false
   - `switch`: Each case, default case
   - `loop`: Empty, single iteration, multiple iterations
   - `call`: Success, failure, exception

**Example Template**:
```python
if decision_type == "if":
    return (f"Test that {function_name}() correctly handles "
            f"when the condition on line {line_number} is false. "
            f"Currently: {source_code}")
```

**Advantages**:
- No API key needed
- Instant response (no network calls)
- Perfect for development
- Deterministic (same input = same output)

---

**Implementation 2: OpenAIClient** (`gaptrace/llm/openai_client.py`)

**Purpose**: Real LLM integration using GPT-4o API

**How It Works**:
1. Requires `OPENAI_API_KEY` environment variable
2. Constructs prompt with:
   - Function context
   - Decision point details
   - Source code snippet
3. Calls OpenAI API (GPT-4o)
4. Returns generated description

**Example Prompt**:
```
Generate a concise test scenario description for:
- Function: validatePayment
- Decision: An if statement on line 42
- Code: if (amount <= 0)
- Coverage: Line 42 is never executed

What test scenario is missing?
```

**Advantages**:
- Intelligent, contextual descriptions
- Understands code semantics
- Can explain complex scenarios
- Production-ready

**Disadvantages**:
- Requires API key
- Network latency
- API costs
- Rate limiting

---

### Layer 3: Data Models

**Location**: `gaptrace/models/decision_point.py`

**Key Classes**:

```python
@dataclass
class DecisionPoint:
    line_number: int
    decision_type: str  # "if", "switch", "loop", "call"
    source_code: str
    is_covered: bool = False

@dataclass
class FunctionAnalysis:
    name: str
    start_line: int
    end_line: int
    decision_points: List[DecisionPoint]

@dataclass
class ParseResult:
    functions: List[FunctionAnalysis]
    file_path: str

@dataclass
class Gap:
    function_name: str
    decision_type: str
    line_number: int
    severity: str  # "critical", "high", "medium", "low"
    source_code: str
    description: str = None
```

---

## Data Flow

### End-to-End Flow with Example

**Input**: `example.cpp` + `example.info` (coverage)

**Step 1: Parse Phase**
```
example.cpp 
    ↓ [AST Parser + libclang]
    ↓ Extracts functions and decision points
    ↓
ParseResult(
    functions=[
        FunctionAnalysis(
            name="validatePayment",
            start_line=10,
            end_line=25,
            decision_points=[
                DecisionPoint(
                    line_number=12,
                    decision_type="if",
                    source_code="if (amount <= 0)"
                ),
                DecisionPoint(
                    line_number=15,
                    decision_type="if",
                    source_code="if (amount > MAX_AMOUNT)"
                ),
                ...
            ]
        ),
        ...
    ]
)
```

**Step 2: Coverage Phase**
```
example.info
    ↓ [LCOV Reader]
    ↓ Parses execution counts
    ↓
CoverageData(
    line_coverage={
        10: 42,   # validatePayment called 42 times
        12: 42,   # if (amount <= 0) always true
        15: 0,    # if (amount > MAX) never executed ← GAP!
        ...
    }
)
```

**Step 3: Analysis Phase**
```
ParseResult + CoverageData
    ↓ [Gap Analyzer]
    ↓ Finds uncovered decisions
    ↓
Gap[](
    Gap(
        function_name="validatePayment",
        decision_type="if",
        line_number=15,
        severity="high",
        source_code="if (amount > MAX_AMOUNT)",
        description=None  # To be filled by LLM
    ),
    ...
)
```

**Step 4: Description Phase**
```
Gap (with line_number=15)
    ↓ [LLM Client - Mock or OpenAI]
    ↓ Generates description
    ↓
Gap(
    ...
    description="Test that validatePayment() correctly rejects " +
                "amounts exceeding MAX_AMOUNT. Currently, the " +
                "code path on line 15 is never executed."
)
```

**Step 5: Output**
```
┌─────────────────────────────────────────────────────────────┐
│ GapTrace Analysis Report                                    │
├─────────────────────────────────────────────────────────────┤
│ File: example.cpp                                           │
│ Functions: 61 | Decision Points: 15 | Gaps Found: 3        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [HIGH] validatePayment() - Line 15 (if)                    │
│ if (amount > MAX_AMOUNT)                                    │
│ ❯ Test that validatePayment() correctly rejects amounts    │
│   exceeding MAX_AMOUNT. Currently, the code path on line 15│
│   is never executed.                                         │
│                                                              │
│ ...                                                          │
└─────────────────────────────────────────────────────────────┘

Optional JSON export: report.json
```

---

## Detailed Component Descriptions

### Parser (`ast_parser.py`)

**Responsibilities**:
- Load C++ source file
- Initialize libclang Index
- Parse file to AST
- Traverse AST to extract functions
- For each function, extract decision points
- Return structured `ParseResult`

**Key Implementation Details**:

```python
def _extract_functions(self):
    """Traverse AST and find all function definitions"""
    for cursor in self.translation_unit.cursor.get_children():
        if cursor.kind == CursorKind.FUNCTION_DECL:
            # Create FunctionAnalysis
            # Recursively find decision points
```

**Decision Point Detection**:
```python
def _is_decision_point(self, cursor):
    """Check if cursor is a control flow decision"""
    return cursor.kind in [
        CursorKind.IF_STMT,
        CursorKind.SWITCH_STMT,
        CursorKind.FOR_STMT,
        CursorKind.WHILE_STMT,
        CursorKind.DO_STMT,
        CursorKind.CALL_EXPR
    ]
```

**Challenge**: Handling C++ syntax complexity
- Nested scopes and braces
- Preprocessor directives
- Macros and templates
- Comments and strings
- libclang handles all of this correctly

---

### Coverage Reader (`lcov_reader.py`)

**Responsibilities**:
- Open and parse `.info` file
- Extract line execution counts
- Validate format
- Build coverage dictionary
- Calculate statistics (coverage %)

**LCOV File Format**:
```
TN:100                    # Total lines
LH:85                     # Lines with hits
LF:100                    # Lines found
DA:1,5                    # Line 1 executed 5 times
DA:2,0                    # Line 2 never executed
DA:3,42                   # Line 3 executed 42 times
end_record
```

**Key Implementation**:
```python
def read_coverage(self, filepath: str) -> CoverageData:
    with open(filepath) as f:
        for line in f:
            if line.startswith('DA:'):
                # Parse "DA:line_num,count"
                parts = line.strip()[3:].split(',')
                line_num = int(parts[0])
                count = int(parts[1])
                self.line_coverage[line_num] = count
```

---

### Gap Analyzer (`gap_analyzer.py`)

**Responsibilities**:
- Combine parse results with coverage data
- Identify uncovered decision points
- Calculate severity scores
- Create Gap objects
- Prepare for LLM description

**Severity Algorithm**:
```python
def _calculate_severity(self, decision_point: DecisionPoint) -> str:
    """Score the importance of this gap"""
    
    # Rule 1: Explicitly marked critical functions
    if self._is_critical(decision_point):
        return "critical"
    
    # Rule 2: Loops are high-value test targets
    if decision_point.decision_type in ("for", "while", "do"):
        return "high"
    
    # Rule 3: Switch statements have many branches
    if decision_point.decision_type == "switch":
        return "high"
    
    # Rule 4: Simple if statements
    if decision_point.decision_type == "if":
        return "medium"
    
    # Rule 5: Default for everything else
    return "low"
```

**Example Analysis**:
```
Function: validatePayment (lines 10-30)
Decision Points:
  - Line 12: if (amount <= 0)          [COVERED, execution_count=42]
  - Line 15: if (amount > MAX_AMOUNT)  [UNCOVERED, execution_count=0] → Gap
  - Line 18: if (currency.empty())     [COVERED, execution_count=5]
  
Gaps Found:
  1. validatePayment:15:if → Severity: HIGH
     (Lines with loops would be even higher priority)
```

---

### LLM Clients

**Pattern**: Strategy pattern with abstract base class

**MockLLMClient Flow**:
```
Gap(function="validatePayment", decision_type="if", line=15, source="if (amount > MAX)")
    ↓
MockLLMClient.describe_gap()
    ↓
Template lookup: decision_type="if" → template for if statements
    ↓
Fill template with actual values
    ↓
Return: "Test that validatePayment() correctly handles when the condition on line 15 is false. Currently: if (amount > MAX_AMOUNT)"
```

**OpenAIClient Flow**:
```
Gap(...)
    ↓
Build system prompt (with context)
    ↓
Build user prompt (with specific gap)
    ↓
Call OpenAI API (GPT-4o)
    ↓
Parse response
    ↓
Return description from LLM
```

---

## Design Patterns

### 1. Strategy Pattern (LLM Selection)

**Intent**: Encapsulate algorithms (LLM implementations) to make them interchangeable

**Implementation**:
- Abstract `LLMClient` base class
- Concrete `MockLLMClient` (development strategy)
- Concrete `OpenAIClient` (production strategy)
- CLI chooses strategy at runtime

**Benefits**:
- Easy to add new LLM providers
- Testing without external dependencies
- Runtime flexibility

### 2. Dependency Injection

**Intent**: Dependencies passed in, not created internally

**Example**:
```python
def __init__(self, llm_client: LLMClient):
    self.llm_client = llm_client
    # Can be MockLLMClient or OpenAIClient

# CLI decides which to inject:
if args.openai:
    llm = OpenAIClient()
else:
    llm = MockLLMClient()

analyzer.describe_gaps(llm)
```

**Benefits**:
- Loose coupling
- Easy testing (inject mock)
- Flexible configuration

### 3. Data Class Pattern

**Intent**: Immutable, type-safe data containers

**Implementation**: All models use `@dataclass` decorator
```python
@dataclass
class Gap:
    function_name: str
    decision_type: str
    line_number: int
    severity: str
    source_code: str
    description: str = None
```

**Benefits**:
- Type hints throughout
- Auto-generated `__init__`, `__repr__`, `__eq__`
- Easy serialization to JSON
- Clear contracts

### 4. Pipeline Pattern

**Intent**: Chain processing stages

**Sequence**:
```
Parse → Coverage → Analyze → Describe → Output
```

Each stage has clear inputs/outputs. Easy to:
- Add new stages
- Test individual stages
- Monitor data flow

---

## Module Dependencies

```
gaptrace/
├── cli.py
│   ├── imports: GapAnalyzer
│   ├── imports: MockLLMClient, OpenAIClient
│   ├── imports: ASTParser, LcovReader
│   └── orchestrates all phases
│
├── parser/
│   └── ast_parser.py
│       ├── imports: libclang
│       ├── imports: DecisionPoint, FunctionAnalysis, ParseResult
│       └── no dependencies on other gaptrace modules
│
├── coverage/
│   └── lcov_reader.py
│       ├── imports: CoverageData
│       └── no dependencies on other gaptrace modules
│
├── analyzer/
│   └── gap_analyzer.py
│       ├── imports: ParseResult, CoverageData, Gap
│       ├── imports: LLMClient (abstract)
│       └── depends on: models, llm.base_client
│
├── llm/
│   ├── base_client.py (abstract interface)
│   │   └── no dependencies
│   ├── mock_client.py
│   │   └── imports: LLMClient
│   └── openai_client.py
│       ├── imports: LLMClient
│       └── imports: openai library
│
└── models/
    └── decision_point.py (data containers)
        └── no dependencies on other modules
```

**Key Observations**:
- Parser and Coverage Reader are independent
- Analyzer depends on both Parser and Coverage Reader
- LLM clients are independent of analysis logic
- CLI orchestrates all layers
- Models are dependency-free (bottom layer)

---

## Example Walkthrough

### Real Example: validatePayment Function

**Source Code** (`example.cpp`):
```cpp
bool validatePayment(double amount, const string& currency) {
    // Line 12-13: First decision point
    if (amount <= 0) {
        cout << "Invalid amount" << endl;
        return false;
    }
    
    // Line 15-18: Second decision point (UNTESTED)
    if (amount > 1000000) {
        cout << "Amount too large" << endl;
        return false;
    }
    
    // Line 20-21: Third decision point
    if (currency.empty()) {
        return false;
    }
    
    // Line 23: Function call decision point
    if (!isKnownCurrency(currency)) {
        return false;
    }
    
    return true;
}
```

**Coverage Report** (`example.info` excerpt):
```
DA:10,50      # validatePayment called 50 times
DA:12,50      # if (amount <= 0) always takes this branch
DA:13,25      # Only 25 calls have amount <= 0
DA:15,0       # if (amount > 1000000) NEVER executed
DA:20,50      # if (currency.empty()) always checked
DA:23,49      # isKnownCurrency called 49 times
```

### Phase 1: Parse
```
ParseResult(
    functions=[
        FunctionAnalysis(
            name="validatePayment",
            start_line=10,
            end_line=27,
            decision_points=[
                DecisionPoint(line=12, type="if", source="if (amount <= 0)"),
                DecisionPoint(line=15, type="if", source="if (amount > 1000000)"),
                DecisionPoint(line=20, type="if", source="if (currency.empty())"),
                DecisionPoint(line=23, type="call", source="if (!isKnownCurrency(currency))"),
            ]
        )
    ]
)
```

### Phase 2: Coverage
```
CoverageData(
    line_coverage={
        10: 50,    # function called
        12: 50,    # line executed
        13: 25,    # line executed
        15: 0,     # ← THIS IS THE GAP
        20: 50,
        23: 49,
    }
)
```

### Phase 3: Analyze
```
Gap[](
    Gap(
        function_name="validatePayment",
        decision_type="if",
        line_number=15,
        severity="high",        # if statements are medium, but let's say it was critical
        source_code="if (amount > 1000000)",
        description=None
    )
)
```

### Phase 4: Describe

**With MockLLMClient**:
```
description = "Test that validatePayment() correctly handles " +
              "when the condition on line 15 is false. " +
              "Currently: if (amount > 1000000)"
```

**With OpenAIClient** (more intelligent):
```
description = "Test the edge case where payment amounts exceed " +
              "the maximum limit (>1,000,000). The current test " +
              "suite never exercises the validation on line 15, " +
              "leaving a critical business logic gap."
```

### Phase 5: Output
```
[HIGH] validatePayment() - Line 15 (if)
if (amount > 1000000)
❯ Test that validatePayment() correctly handles when the condition 
  on line 15 is false. Currently: if (amount > 1000000)

[MEDIUM] validatePayment() - Line 20 (if)
if (currency.empty())
❯ Test that validatePayment() correctly handles when the condition 
  on line 20 is false. Currently: if (currency.empty())
```

---

## Summary

**GapTrace Architecture** is built on:
1. **Separation of Concerns**: Each module has one responsibility
2. **Clean Interfaces**: Abstract LLMClient enables flexibility
3. **Data-Driven Design**: Clear data models throughout
4. **Pipeline Pattern**: Sequential processing stages
5. **Strategy Pattern**: Pluggable implementations (Mock vs OpenAI)

**Flow**: Source Code → Parse → Coverage Map → Analyze → Describe → Report

**Result**: Actionable insights about missing test scenarios, powered by intelligent analysis and LLM descriptions.
