# 🔍 GapTrace

> **Coverage tells you what ran. GapTrace tells you what didn’t — and why it matters.**

GapTrace is a developer-first CLI + VS Code extension that detects **missing unit test scenarios** in C/C++ codebases.

It doesn’t generate tests.  
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
“What lines were executed?”

But they don’t answer:
“What important scenarios were never tested?”

---

## 💡 The GapTrace Approach

GapTrace flips the perspective:

Instead of asking “what is covered?”  
It asks 👉 “what logical paths are missing?”

---

## 🧠 How It Works

Code → AST → Logic Graph → Test Mapping → Gap Detection → Risk Analysis

1. Parse code (AST-based)  
2. Build logical paths  
3. Map existing tests  
4. Detect gaps  
5. Explain impact  

---

## ⚙️ Features

- Untested branches detection  
- Edge case identification  
- Missing negative scenarios  
- Risk scoring  
- Explainable insights  

---

## 🧪 Example

### Code

```cpp
int processPayment(int amount) {
    if (amount <= 0) return -1;
    if (!gatewayAvailable()) return -2;
    return charge(amount);
}
```

### Output

Function: processPayment()

Missing:
- amount = 0  
- amount < 0  
- gateway failure  

Risk: HIGH

---

## 🛠️ Tech Stack

- Python CLI  
- Clang AST  
- Static analysis  

---

## 🚀 Usage (Planned)

pip install gaptrace  
gaptrace scan ./src  
gaptrace report  

---

## 🧭 Vision

Move from “Did we test enough?” to “Did we test the right things?”
