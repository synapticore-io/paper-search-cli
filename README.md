# Paper Search MCP

A Model Context Protocol (MCP) server for searching and downloading academic papers from multiple sources, including arXiv, PubMed, bioRxiv, and Sci-Hub (optional). Designed for seamless integration with large language models like Claude Desktop.

![PyPI](https://img.shields.io/pypi/v/paper-search-mcp.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
[![smithery badge](https://smithery.ai/badge/@openags/paper-search-mcp)](https://smithery.ai/server/@openags/paper-search-mcp)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
  - [Quick Start](#quick-start)
    - [Install Package](#install-package)
    - [Configure Claude Desktop](#configure-claude-desktop)
  - [For Development](#for-development)
    - [Setup Environment](#setup-environment)
    - [Install Dependencies](#install-dependencies)
- [CLI Usage](#cli-usage)
- [Contributing](#contributing)
- [Demo](#demo)
- [License](#license)
- [TODO](#todo)

---

## Overview

`paper-search-mcp` is a Python-based MCP server and CLI tool that enables users to search and download academic papers from various platforms. It provides both an MCP server for LLM integration and a command-line interface for direct usage. Built with FastMCP and httpx, it offers async performance and seamless integration with AI-driven workflows.

---

## Features

- **Multi-Source Support**: Search and download papers from arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR ePrint Archive, Semantic Scholar, CrossRef.
- **Command-Line Interface**: Use `paper-search` command for searching, downloading, and reading papers.
- **Standardized Output**: Papers are returned in a consistent dictionary format via the `Paper` class.
- **Asynchronous Performance**: All operations use `httpx` with async/await for efficient network requests.
- **MCP Integration**: Compatible with MCP clients like Claude Desktop for LLM context enhancement.
- **Extensible Design**: Easily add new academic platforms by extending the `academic_platforms` module.

---

## Installation

`paper-search-mcp` can be installed using `uv` or `pip`. Below are two approaches: a quick start for immediate use and a detailed setup for development.

### Installing via Smithery

To install paper-search-mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@openags/paper-search-mcp):

```bash
npx -y @smithery/cli install @openags/paper-search-mcp --client claude
```

### Quick Start

For users who want to quickly run the server:

1. **Install Package**:

   ```bash
   uv add paper-search-mcp
   ```

2. **Configure Claude Desktop**:
   Add this configuration to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):
   ```json
   {
     "mcpServers": {
       "paper_search_server": {
         "command": "uv",
         "args": [
           "run",
           "--directory",
           "/path/to/your/paper-search-mcp",
           "-m",
           "paper_search_mcp.server"
         ],
         "env": {
           "SEMANTIC_SCHOLAR_API_KEY": "" // Optional: For enhanced Semantic Scholar features
         }
       }
     }
   }
   ```
   > Note: Replace `/path/to/your/paper-search-mcp` with your actual installation path.

### For Development

For developers who want to modify the code or contribute:

1. **Setup Environment**:

   ```bash
   # Install uv if not installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Clone repository
   git clone https://github.com/openags/paper-search-mcp.git
   cd paper-search-mcp

   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**:

   ```bash
   # Install project in editable mode
   uv add -e .

   # Add development dependencies (optional)
   uv add pytest flake8
   ```

---

## CLI Usage

After installation, you can use the `paper-search` command to search and download papers directly from your terminal:

### Search for papers

```bash
# Search arXiv for machine learning papers
paper-search search "machine learning" --source arxiv --max-results 10

# Search PubMed for COVID-19 research
paper-search search "COVID-19" --source pubmed --max-results 20

# Search bioRxiv
paper-search search "neural networks" --source biorxiv
```

### Download papers

```bash
# Download an arXiv paper
paper-search download 2106.12345 --source arxiv --output ./papers

# Download from bioRxiv
paper-search download 10.1101/2021.01.01.123456 --source biorxiv
```

### Read paper text

```bash
# Read and extract text from a paper
paper-search read 2106.12345 --source arxiv

# Show full text
paper-search read 2106.12345 --source arxiv --all
```

### List available sources

```bash
# See all supported paper sources
paper-search list-sources
```

### Available sources

- `arxiv` - arXiv preprint repository (search, download, read)
- `pubmed` - PubMed biomedical literature (search)
- `biorxiv` - bioRxiv biology preprints (search, download, read)
- `medrxiv` - medRxiv health sciences preprints (search, download, read)
- `google-scholar` - Google Scholar (search)
- `iacr` - IACR ePrint cryptology archive (search, download, read)
- `semantic` - Semantic Scholar AI research tool (search, download, read)
- `crossref` - CrossRef citation service (search)

---

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the Repository**:
   Click "Fork" on GitHub.

2. **Clone and Set Up**:

   ```bash
   git clone https://github.com/yourusername/paper-search-mcp.git
   cd paper-search-mcp
   pip install -e ".[dev]"  # Install dev dependencies (if added to pyproject.toml)
   ```

3. **Make Changes**:

   - Add new platforms in `academic_platforms/`.
   - Update tests in `tests/`.

4. **Submit a Pull Request**:
   Push changes and create a PR on GitHub.

---

## Demo

<img src="docs\images\demo.png" alt="Demo" width="800">

## TODO

### Planned Academic Platforms

- [√] arXiv
- [√] PubMed
- [√] bioRxiv
- [√] medRxiv
- [√] Google Scholar
- [√] IACR ePrint Archive
- [√] Semantic Scholar
- [ ] PubMed Central (PMC)
- [ ] Science Direct
- [ ] Springer Link
- [ ] IEEE Xplore
- [ ] ACM Digital Library
- [ ] Web of Science
- [ ] Scopus
- [ ] JSTOR
- [ ] ResearchGate
- [ ] CORE
- [ ] Microsoft Academic

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Happy researching with `paper-search-mcp`! If you encounter issues, open a GitHub issue.
