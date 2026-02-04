# Paper-Verify

**Validate academic paper claims against your actual results.**

[![CI](https://github.com/rakaarao17/Paper-Verify/actions/workflows/ci.yml/badge.svg)](https://github.com/rakaarao17/Paper-Verify/actions)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A CLI tool that automatically checks if numeric claims in your LaTeX paper match your experiment result files. Helps prevent typos, rounding errors, and outdated figures in academic writing.

## 🎯 Problem

Researchers often introduce errors when writing papers:

- Typos in reported metrics
- Outdated figures after re-running experiments
- Rounding inconsistencies

Manual verification is tedious and error-prone.

## ✨ Solution

```bash
paperverify check paper.tex --results results/

# Output:
# ✅ Line 60: "MAE of 2.10" matches chronos-small_etth1.json
# ✅ Line 60: "XGBoost's 2.44" matches xgboost_etth1.json
# ⚠️ Line 282: "0.00013" differs from 0.000135 (2% off)
```

## 🚀 Installation

```bash
pip install paper-verify
```

## 📖 Usage

### Basic Check

```bash
paperverify check paper.tex --results results/
```

### With Tolerance

```bash
paperverify check paper.tex --results results/ --tolerance 5
```

### Generate Report

```bash
paperverify check paper.tex --results results/ --report report.md
```

## 📁 Supported Formats (All Built-in)

| Paper  | Results                                              |
| ------ | ---------------------------------------------------- |
| `.tex` | `.json`, `.csv`, `.sqlite`, `.db`, `.pkl`, `.pickle` |
| `.md`  | `.xlsx`, `.xls`, `.docx`, `.yaml`, `.yml`, `.pdf`\*  |

_\*PDF support requires Java 8+ installed on your system_

All formats work out of the box — no extras needed!

## 🛠️ Development

```bash
git clone https://github.com/rakaarao17/Paper-Verify
cd Paper-Verify
pip install -e ".[dev]"
pytest
```

## 📝 License

MIT License
