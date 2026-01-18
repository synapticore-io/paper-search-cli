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

`paper-search-mcp` is a Python-based MCP server and CLI tool for searching and downloading academic papers from multiple platforms.

### What This Tool Does
- **For Users**: Command-line tool (`paper-search`) to search, download, and read academic papers from 8+ sources
- **For AI/LLMs**: MCP server that exposes paper search capabilities as tools for AI assistants like Claude
- **For Developers**: Extensible platform for adding new academic paper sources

### Key Capabilities
1. **Search**: Query papers by keywords across multiple academic databases
2. **Download**: Retrieve full-text PDFs where available
3. **Read**: Extract and return text content from papers
4. **Integrate**: Connect with AI assistants via Model Context Protocol (MCP)

### Architecture
```
User/AI → CLI/MCP Server → Platform Searchers → Academic APIs → Papers
                ↓                    ↓
          Typer/FastMCP         httpx async
```

**Components:**
- **CLI** (`cli.py`): Command-line interface using Typer
- **MCP Server** (`server.py`): FastMCP-based server exposing tools
- **Platform Searchers** (`academic_platforms/*.py`): Async API clients for each source
- **Data Model** (`paper.py`): Unified Paper dataclass for all sources

### Supported Platforms
| Platform | Search | Download | Read | Notes |
|----------|--------|----------|------|-------|
| arXiv | ✅ | ✅ | ✅ | Preprint repository |
| PubMed | ✅ | ❌ | ❌ | Metadata only |
| bioRxiv | ✅ | ✅ | ✅ | Biology preprints |
| medRxiv | ✅ | ✅ | ✅ | Medical preprints |
| Google Scholar | ✅ | ❌ | ❌ | Web scraping |
| IACR ePrint | ✅ | ✅ | ✅ | Cryptology papers |
| Semantic Scholar | ✅ | ✅ | ✅ | AI-powered search |
| CrossRef | ✅ | ❌ | ❌ | Citation database |

---

## Features

- **Multi-Source Support**: Search and download papers from arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR ePrint Archive, Semantic Scholar, CrossRef.
- **Command-Line Interface**: Use `paper-search` command for searching, downloading, and reading papers.
- **Standardized Output**: Papers are returned in a consistent dictionary format via the `Paper` class.
- **Asynchronous Performance**: All operations use `httpx` with async/await for efficient network requests.
- **MCP Integration**: Compatible with MCP clients like Claude Desktop for LLM context enhancement.
- **Extensible Design**: Easily add new academic platforms by extending the `academic_platforms` module.
- **Type-Safe**: Full type hints throughout the codebase for better IDE support and error checking.

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

## API Reference

### Paper Data Model

All search results return `Paper` objects with the following structure:

```python
@dataclass
class Paper:
    # Required fields
    paper_id: str              # Unique identifier (e.g., "2106.12345" for arXiv)
    title: str                 # Paper title
    authors: List[str]         # List of author names
    abstract: str              # Abstract text
    doi: str                   # Digital Object Identifier
    published_date: datetime   # Publication date
    pdf_url: str               # Direct PDF download link
    url: str                   # URL to paper page
    source: str                # Source platform (e.g., "arxiv", "pubmed")
    
    # Optional fields
    updated_date: Optional[datetime] = None
    categories: List[str] = None       # Subject categories
    keywords: List[str] = None         # Paper keywords
    citations: int = 0                 # Citation count
    references: Optional[List[str]] = None
    extra: Optional[Dict] = None       # Platform-specific metadata
```

### CLI Commands

#### search
```bash
paper-search search <query> [OPTIONS]

Arguments:
  query          Search query string (required)

Options:
  --source, -s   Source platform [default: arxiv]
                 Choices: arxiv, pubmed, biorxiv, medrxiv, google-scholar, 
                         iacr, semantic, crossref
  --max-results  Maximum results to return [default: 10]
  --year, -y     Filter by publication year (CrossRef only)

Returns:
  Table of papers with ID, title, authors, and year
```

#### download
```bash
paper-search download <paper_id> [OPTIONS]

Arguments:
  paper_id       Paper ID from the source platform (required)

Options:
  --source, -s   Source platform [default: arxiv]
                 Supported: arxiv, biorxiv, medrxiv, iacr, semantic
  --output, -o   Output directory [default: ./downloads]

Returns:
  Path to downloaded PDF file
```

#### read
```bash
paper-search read <paper_id> [OPTIONS]

Arguments:
  paper_id       Paper ID from the source platform (required)

Options:
  --source, -s   Source platform [default: arxiv]
                 Supported: arxiv, biorxiv, medrxiv, iacr, semantic
  --output, -o   Directory for PDF storage [default: ./downloads]
  --all, -a      Show full text (default: first 1000 chars)

Returns:
  Extracted text content from the paper
```

#### list-sources
```bash
paper-search list-sources

Returns:
  Table of all available sources with capabilities
```

### MCP Server Tools

When running as an MCP server, the following tools are exposed:

| Tool Name | Parameters | Returns | Description |
|-----------|------------|---------|-------------|
| `search_arxiv` | `query: str, max_results: int` | `List[Dict]` | Search arXiv papers |
| `search_pubmed` | `query: str, max_results: int` | `List[Dict]` | Search PubMed papers |
| `search_biorxiv` | `query: str, max_results: int` | `List[Dict]` | Search bioRxiv papers |
| `search_medrxiv` | `query: str, max_results: int` | `List[Dict]` | Search medRxiv papers |
| `search_google_scholar` | `query: str, max_results: int` | `List[Dict]` | Search Google Scholar |
| `search_iacr` | `query: str, max_results: int, fetch_details: bool` | `List[Dict]` | Search IACR ePrint |
| `search_semantic` | `query: str, max_results: int` | `List[Dict]` | Search Semantic Scholar |
| `search_crossref` | `query: str, max_results: int, year: int` | `List[Dict]` | Search CrossRef |
| `download_arxiv` | `paper_id: str, save_path: str` | `str` | Download arXiv PDF |
| `download_biorxiv` | `paper_id: str, save_path: str` | `str` | Download bioRxiv PDF |
| `download_medrxiv` | `paper_id: str, save_path: str` | `str` | Download medRxiv PDF |
| `download_iacr` | `paper_id: str, save_path: str` | `str` | Download IACR PDF |
| `download_semantic` | `paper_id: str, save_path: str` | `str` | Download from Semantic Scholar |
| `read_arxiv_paper` | `paper_id: str, save_path: str` | `str` | Extract text from arXiv paper |
| `read_biorxiv_paper` | `paper_id: str, save_path: str` | `str` | Extract text from bioRxiv paper |
| `read_medrxiv_paper` | `paper_id: str, save_path: str` | `str` | Extract text from medRxiv paper |
| `read_iacr_paper` | `paper_id: str, save_path: str` | `str` | Extract text from IACR paper |
| `read_semantic_paper` | `paper_id: str, save_path: str` | `str` | Extract text from Semantic Scholar |

### Python API

For programmatic use:

```python
import asyncio
from paper_search_mcp.academic_platforms.arxiv import ArxivSearcher

async def search_papers():
    searcher = ArxivSearcher()
    papers = await searcher.search("quantum computing", max_results=5)
    
    for paper in papers:
        print(f"{paper.title} by {', '.join(paper.authors[:3])}")
        print(f"Published: {paper.published_date.year}")
        print(f"URL: {paper.url}\n")

asyncio.run(search_papers())
```

---

## Troubleshooting

### Common Issues

**Issue: "Module not found" error**
```bash
# Solution: Install the package in editable mode
pip install -e .
```

**Issue: "httpx.ConnectError" or network errors**
```bash
# Solution: Check internet connection and firewall settings
# Some platforms may require specific network access
```

**Issue: CLI command not found after installation**
```bash
# Solution: Ensure the package is installed and in PATH
pip install -e .
# Or use: python -m paper_search_mcp.cli search "query"
```

**Issue: PDF download fails**
```bash
# Solution: Not all platforms support PDF downloads
# Check the platform capabilities table above
paper-search list-sources  # See which platforms support downloads
```

### Platform-Specific Notes

- **arXiv**: Most reliable for downloads, IDs like "2106.12345"
- **PubMed**: Metadata only, use DOI to access publisher site
- **Google Scholar**: Rate-limited, use sparingly
- **Semantic Scholar**: Requires API key for enhanced features (set `SEMANTIC_SCHOLAR_API_KEY` env var)
- **CrossRef**: Citation database, no PDFs

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
