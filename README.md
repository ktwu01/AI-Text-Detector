# AI-Text-Highlighter
---
Author: Koutian Wu

Github, LinkedIn: ktwu01

Release date: Apr 20, 2025

---

The AI Word and Phrase Highlighter is designed to detect common words and phrases frequently used in AI-generated content.

### How it works

1. The tool maintains a database of words and phrases commonly used by AI systems like ChatGPT, Claude, and others.
2. When you input text, it scans for these markers and highlights them.
3. It also provides statistics on the frequency of these markers in your text.

### Use cases

- Writers can use this to reduce AI-like patterns in their writing
- Content reviewers can quickly identify potential AI-generated content
- Students and educators can ensure original work
- SEO specialists can improve content to avoid AI detection penalties

### Sources

The default database includes words and phrases identified by various AI detection tools including:

- ZeroGPT
- GPTZero
- Originality.ai
- And various research studies on AI-generated text patterns

You can extend the database with your own observations or from other sources.

# AI Text Highlighter

A collection of tools for detecting and highlighting common AI-generated words and phrases in text. This tool helps identify content patterns often used by AI models like ChatGPT, Claude, and others.

## Features

- Highlight common AI words and phrases in text
- Analyze the percentage of AI markers in content
- Visualize results with charts and graphs
- Compare AI-generated vs. human-written text
- Export and import word/phrase lists

## Components

- **AI Word Highlighter**: A Streamlit application for interactive analysis
- **Simple AI Word Highlighter**: A lightweight Python class for integration into any project
- **SQL-Based AI Word Manager**: A database tool for managing AI word collections
- **AI SEO Analyzer**: A comprehensive command-line analyzer with reporting capabilities

## Installation

The code is not publicly available in this repository, but requires the following dependencies:

```bash
pip install pandas matplotlib seaborn streamlit
```
