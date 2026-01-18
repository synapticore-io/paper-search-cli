# GitHub Copilot Instructions for paper-search-mcp

## Quick Reference

**Purpose**: MCP server and CLI tool for searching and downloading academic papers from multiple sources

**Key Files**:
- `server.py` - MCP server with FastMCP tools
- `cli.py` - Typer CLI commands
- `paper.py` - Paper dataclass model
- `academic_platforms/*.py` - Platform-specific searchers

**Architecture Pattern**: Async throughout
- Platform searchers: async methods using httpx
- Server: FastMCP with async tools
- CLI: asyncio.run() wrapper for commands

---

## Project Overview

This is a Model Context Protocol (MCP) server for searching and downloading academic papers from multiple sources, including arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR ePrint Archive, Semantic Scholar, and CrossRef.

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| HTTP Client | httpx | Async HTTP requests to academic APIs |
| MCP Framework | FastMCP | Model Context Protocol server |
| CLI Framework | typer | Command-line interface |
| Terminal UI | rich | Enhanced terminal output |
| HTML Parsing | BeautifulSoup4 + lxml | Parsing academic website data |
| PDF Processing | PyPDF2 | Text extraction from PDFs |
| Testing | unittest | Unit tests |
| Type Checking | Python 3.10+ type hints | Static type safety |

### Project Structure

```
paper-search-mcp/
├── paper_search_mcp/          # Main package
│   ├── server.py              # MCP server (FastMCP)
│   ├── cli.py                 # CLI tool (Typer)
│   ├── paper.py               # Paper dataclass
│   └── academic_platforms/    # Platform searchers
│       ├── arxiv.py           # arXiv searcher
│       ├── pubmed.py          # PubMed searcher
│       ├── biorxiv.py         # bioRxiv searcher
│       ├── medrxiv.py         # medRxiv searcher
│       ├── google_scholar.py  # Google Scholar searcher
│       ├── iacr.py            # IACR ePrint searcher
│       ├── semantic.py        # Semantic Scholar searcher
│       ├── crossref.py        # CrossRef searcher
│       └── sci_hub.py         # Sci-Hub (optional)
├── tests/                     # Unit tests
│   ├── test_arxiv.py
│   ├── test_server.py
│   └── ...
├── docs/                      # Documentation
├── .github/                   # GitHub configuration
│   └── copilot-instructions.md
├── pyproject.toml            # Package configuration
└── README.md                 # User documentation
```

### Data Flow

```
┌─────────────┐
│ User / AI   │
└──────┬──────┘
       │
       ├──────────┐
       ↓          ↓
┌──────────┐ ┌────────┐
│   CLI    │ │  MCP   │
│  (typer) │ │ Server │
└────┬─────┘ └───┬────┘
     │           │
     └─────┬─────┘
           ↓
    ┌──────────────┐
    │  Platform    │
    │  Searchers   │
    │  (async)     │
    └──────┬───────┘
           │
           ↓
    ┌──────────────┐
    │ httpx Client │
    └──────┬───────┘
           │
           ↓
    ┌──────────────┐
    │ Academic APIs│
    │ (arXiv, etc) │
    └──────────────┘
```

---

## How Things Work

### Request Flow (Search Operation)

1. **User initiates search**:
   - CLI: `paper-search search "quantum computing" --source arxiv`
   - MCP: AI calls `search_arxiv(query="quantum computing")`

2. **Command routing**:
   - CLI: `search()` function in `cli.py`
   - MCP: `@mcp.tool()` decorated function in `server.py`

3. **Platform searcher execution**:
   ```python
   async def search(query: str, max_results: int = 10) -> List[Paper]:
       async with httpx.AsyncClient() as client:
           response = await client.get(API_URL, params={...})
           response.raise_for_status()
           # Parse response
           return [Paper(...) for item in results]
   ```

4. **Response formatting**:
   - CLI: Display as rich table
   - MCP: Convert to `List[Dict]` via `paper.to_dict()`

5. **Return to user**:
   - CLI: Formatted table output
   - MCP: JSON response to AI assistant

### Async Pattern

**All platform searchers follow this pattern:**

```python
class PlatformSearcher:
    async def search(self, query: str, max_results: int) -> List[Paper]:
        """Search for papers - always async"""
        async with httpx.AsyncClient() as client:
            # Make HTTP request
            response = await client.get(url, params=params)
            response.raise_for_status()
            # Parse and return
            return papers
    
    async def download_pdf(self, paper_id: str, save_path: str) -> str:
        """Download PDF - always async"""
        async with httpx.AsyncClient() as client:
            response = await client.get(pdf_url)
            # Save file
            return file_path
    
    async def read_paper(self, paper_id: str, save_path: str) -> str:
        """Extract text - always async"""
        # Download if needed, then extract
        return text_content
```

**MCP Server wraps searchers:**

```python
@mcp.tool()
async def search_platform(query: str, max_results: int = 10) -> List[Dict]:
    """MCP tool - always async"""
    papers = await platform_searcher.search(query, max_results)
    return [paper.to_dict() for paper in papers]
```

**CLI wraps with asyncio.run():**

```python
@app.command()
def search(query: str, source: str = "arxiv"):
    """CLI command - synchronous wrapper"""
    async def run():
        papers = await searcher.search(query)
        display_papers(papers)
    asyncio.run(run())
```

### Paper Data Model

**All searchers must return Paper objects:**

```python
from datetime import datetime
from typing import List

paper = Paper(
    paper_id="2106.12345",           # Required: unique ID
    title="Paper Title",              # Required
    authors=["Author 1", "Author 2"], # Required: list
    abstract="Abstract text...",      # Required
    doi="10.1234/example",           # Required: empty string if none
    published_date=datetime.now(),   # Required: datetime object
    pdf_url="https://...",           # Required: empty string if none
    url="https://...",               # Required: paper landing page
    source="arxiv",                  # Required: platform name
    # Optional fields
    categories=["cs.AI", "cs.LG"],
    keywords=["AI", "ML"],
    citations=42
)
```

---

## Build and Test Commands

**Installing dependencies:**
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv add -e .

# Or using pip
pip install -e .
```

**Using the CLI:**
```bash
# Search for papers
paper-search search "machine learning" --source arxiv --max-results 10

# Download a paper
paper-search download 2106.12345 --source arxiv --output ./downloads

# Read paper text
paper-search read 2106.12345 --source arxiv

# List available sources
paper-search list-sources
```

**Running tests:**
```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test file
python -m unittest tests.test_arxiv
python -m unittest tests.test_server

# Run specific test method
python -m unittest tests.test_arxiv.TestArxivSearcher.test_search
```

**Building the package:**
```bash
python -m pip install build
python -m build
```

**Running the MCP server:**
```bash
# For development
uv run -m paper_search_mcp.server

# For production (after installation)
python -m paper_search_mcp.server
```

## Coding Conventions and Rules

### General Python Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Python 3.10+ features are acceptable
- Use descriptive variable names

### Code Organization
- Each academic platform should have its own module in `academic_platforms/`
- All searchers should return `Paper` objects or lists of `Paper` objects
- Use the `Paper` class defined in `paper.py` for consistent data structure
- All searcher methods (search, download_pdf, read_paper) are async and use httpx
- Use relative imports within the package: `from ..paper import Paper` (from academic_platforms/)
- Platform searchers use `httpx` library with async/await pattern
- Server.py uses FastMCP framework to expose async searcher methods as MCP tools
- CLI module uses typer to provide command-line interface to all search/download functions

### Testing Requirements
- Each platform searcher should have a corresponding test file in `tests/`
- Test files should be named `test_<platform>.py`
- Use `unittest.TestCase` for test classes
- Tests should verify that search results return the expected structure
- Include basic functionality tests (search, download where applicable)

### File Modification Guidelines
- **DO NOT** modify:
  - `LICENSE` file
  - `.gitignore` unless adding necessary exceptions
  - `uv.lock` directly (managed by uv)
  - Existing working tests unless fixing bugs

- **CAREFUL** when modifying:
  - `server.py` - core MCP server, changes affect all tools
  - `paper.py` - data model used across all platforms

### Adding New Academic Platforms

**Complete Step-by-Step Guide:**

#### Step 1: Create Platform Searcher

Create `academic_platforms/newplatform.py`:

```python
# academic_platforms/newplatform.py
from typing import List
from datetime import datetime
import httpx
from ..paper import Paper

class NewPlatformSearcher:
    """
    Searcher for NewPlatform academic database.
    
    API Documentation: https://newplatform.com/api/docs
    Rate Limits: 100 requests/minute
    Authentication: API key (optional)
    """
    
    BASE_URL = "https://api.newplatform.com/v1"
    
    def __init__(self, api_key: str = None):
        """
        Initialize searcher.
        
        Args:
            api_key: Optional API key for enhanced features
        """
        self.api_key = api_key
        self.headers = {"API-Key": api_key} if api_key else {}
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers on NewPlatform.
        
        Args:
            query: Search query string (keywords, titles, etc.)
            max_results: Maximum number of results to return (1-100)
            
        Returns:
            List of Paper objects with standardized fields
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        # Build request parameters
        params = {
            'q': query,
            'limit': max_results,
            'format': 'json'
        }
        
        # Make async HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/search",
                params=params,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
        
        # Parse response into Paper objects
        papers = []
        for item in data.get('results', []):
            try:
                # Extract required fields
                paper_id = item['id']
                title = item['title']
                authors = [a['name'] for a in item.get('authors', [])]
                abstract = item.get('abstract', '')
                doi = item.get('doi', '')
                
                # Parse date (adjust format as needed)
                pub_date_str = item.get('published', '')
                published_date = datetime.fromisoformat(pub_date_str) if pub_date_str else datetime.now()
                
                # Get URLs
                pdf_url = item.get('pdf_url', '')
                url = item.get('url', f"{self.BASE_URL}/papers/{paper_id}")
                
                # Create Paper object
                papers.append(Paper(
                    paper_id=paper_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    doi=doi,
                    published_date=published_date,
                    pdf_url=pdf_url,
                    url=url,
                    source='newplatform',
                    # Optional fields
                    categories=item.get('categories', []),
                    keywords=item.get('keywords', []),
                    citations=item.get('citation_count', 0)
                ))
            except (KeyError, ValueError) as e:
                print(f"Error parsing paper: {e}")
                continue
        
        return papers
    
    async def download_pdf(self, paper_id: str, save_path: str) -> str:
        """
        Download PDF for a paper.
        
        Args:
            paper_id: Platform-specific paper ID
            save_path: Directory to save the PDF
            
        Returns:
            Path to downloaded PDF file
            
        Raises:
            httpx.HTTPError: If download fails
            NotImplementedError: If platform doesn't support downloads
        """
        pdf_url = f"{self.BASE_URL}/papers/{paper_id}/pdf"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(pdf_url, headers=self.headers)
            response.raise_for_status()
        
        # Save PDF
        output_file = f"{save_path}/{paper_id}.pdf"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        return output_file
    
    async def read_paper(self, paper_id: str, save_path: str = "./downloads") -> str:
        """
        Read and extract text from a paper PDF.
        
        Args:
            paper_id: Platform-specific paper ID
            save_path: Directory where PDF is/will be saved
            
        Returns:
            Extracted text content
            
        Raises:
            Exception: If PDF reading fails
        """
        import os
        from PyPDF2 import PdfReader
        
        # Download if not exists
        pdf_path = f"{save_path}/{paper_id}.pdf"
        if not os.path.exists(pdf_path):
            pdf_path = await self.download_pdf(paper_id, save_path)
        
        # Extract text
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
```

#### Step 2: Add to MCP Server

Edit `server.py`:

```python
# Add import at top
from .academic_platforms.newplatform import NewPlatformSearcher

# Add searcher instance
newplatform_searcher = NewPlatformSearcher()

# Add MCP tools
@mcp.tool()
async def search_newplatform(query: str, max_results: int = 10) -> List[Dict]:
    """
    Search academic papers from NewPlatform.
    
    Args:
        query: Search query string (e.g., 'machine learning').
        max_results: Maximum number of papers to return (default: 10).
    
    Returns:
        List of paper metadata in dictionary format.
    """
    papers = await newplatform_searcher.search(query, max_results)
    return [paper.to_dict() for paper in papers]

@mcp.tool()
async def download_newplatform(paper_id: str, save_path: str = "./downloads") -> str:
    """
    Download PDF of a NewPlatform paper.
    
    Args:
        paper_id: NewPlatform paper ID.
        save_path: Directory to save the PDF (default: './downloads').
    
    Returns:
        Path to the downloaded PDF file.
    """
    return await newplatform_searcher.download_pdf(paper_id, save_path)

@mcp.tool()
async def read_newplatform_paper(paper_id: str, save_path: str = "./downloads") -> str:
    """
    Read and extract text from a NewPlatform paper PDF.
    
    Args:
        paper_id: NewPlatform paper ID.
        save_path: Directory where the PDF is/will be saved.
    
    Returns:
        The extracted text content of the paper.
    """
    return await newplatform_searcher.read_paper(paper_id, save_path)
```

#### Step 3: Add to CLI

Edit `cli.py`:

```python
# Add import at top
from .academic_platforms.newplatform import NewPlatformSearcher

# Add searcher instance
newplatform_searcher = NewPlatformSearcher()

# Update searchers dict in search() command
searchers = {
    # ... existing searchers ...
    "newplatform": newplatform_searcher,
}

# Update list_sources() command
sources = [
    # ... existing sources ...
    ("newplatform", "NewPlatform - Academic database", "search, download, read"),
]
```

#### Step 4: Create Tests

Create `tests/test_newplatform.py`:

```python
# tests/test_newplatform.py
import unittest
import asyncio
from paper_search_mcp.academic_platforms.newplatform import NewPlatformSearcher

class TestNewPlatformSearcher(unittest.TestCase):
    def test_search(self):
        """Test that search returns expected number of results."""
        searcher = NewPlatformSearcher()
        papers = asyncio.run(searcher.search("machine learning", max_results=5))
        
        # Assertions
        self.assertIsInstance(papers, list)
        self.assertLessEqual(len(papers), 5)
        
        if papers:
            paper = papers[0]
            self.assertTrue(paper.title)
            self.assertTrue(paper.paper_id)
            self.assertEqual(paper.source, 'newplatform')
            self.assertIsInstance(paper.authors, list)

    def test_search_handles_errors(self):
        """Test that search handles API errors gracefully."""
        searcher = NewPlatformSearcher()
        # Invalid query should return empty list, not crash
        papers = asyncio.run(searcher.search("", max_results=1))
        self.assertIsInstance(papers, list)

if __name__ == '__main__':
    unittest.main()
```

#### Step 5: Update Documentation

Update `README.md` TODO section:
```markdown
- [√] NewPlatform
```

Update supported platforms table in README and copilot-instructions.

---

### Example: Platform Searcher Implementation (Simple)

```python
# academic_platforms/example.py
from typing import List
from datetime import datetime
import httpx
from ..paper import Paper

class ExampleSearcher:
    """Searcher for Example Platform."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.example.com"
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers on Example Platform.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of Paper objects
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url,
                params={'q': query, 'limit': max_results}
            )
            response.raise_for_status()
            data = response.json()
            
        papers = []
        for item in data['results']:
            papers.append(Paper(
                paper_id=item['id'],
                title=item['title'],
                authors=item['authors'],
                abstract=item['abstract'],
                doi=item.get('doi', ''),
                published_date=datetime.fromisoformat(item['date']),
                pdf_url=item.get('pdf_url', ''),
                url=item['url'],
                source='example'
            ))
        return papers
    
    async def download_pdf(self, paper_id: str, save_path: str) -> str:
        """Download PDF for a paper."""
        pdf_url = f"{self.base_url}/papers/{paper_id}/pdf"
        async with httpx.AsyncClient() as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
        
        output_file = f"{save_path}/{paper_id}.pdf"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return output_file
```

### Example: MCP Tool Definition

```python
# In server.py
from .academic_platforms.example import ExampleSearcher

example_searcher = ExampleSearcher()

@mcp.tool()
async def search_example(query: str, max_results: int = 10) -> List[Dict]:
    """Search academic papers from Example Platform.
    
    Args:
        query: Search query string (e.g., 'machine learning').
        max_results: Maximum number of papers to return (default: 10).
        
    Returns:
        List of dictionaries with paper metadata.
    """
    return await async_search(example_searcher, query, max_results)
```

### Example: Unit Test

```python
# tests/test_example.py
import unittest
from paper_search_mcp.academic_platforms.example import ExampleSearcher

class TestExampleSearcher(unittest.TestCase):
    def test_search(self):
        searcher = ExampleSearcher()
        papers = searcher.search("machine learning", max_results=10)
        self.assertEqual(len(papers), 10)
        self.assertTrue(papers[0].title)
        
if __name__ == '__main__':
    unittest.main()
```

## Security Considerations

- Never commit API keys or secrets to the repository
- API keys should be passed through environment variables
- Validate and sanitize user inputs in search queries
- Be cautious with file downloads - validate paths and content
- Rate limit API calls to external services when possible

## Common Patterns

### Platform searchers use httpx with async/await
```python
import httpx
from typing import List

async def search(self, query: str, max_results: int = 10) -> List[Paper]:
    """Search implementation using httpx."""
    async with httpx.AsyncClient() as client:
        response = await client.get(self.BASE_URL, params={'q': query})
        response.raise_for_status()
        # Process response
    return papers
```

### Server exposes async searchers as MCP tools
```python
# In server.py
async def async_search(searcher, query: str, max_results: int, **kwargs) -> List[Dict]:
    # Searchers now use httpx internally and are async
    papers = await searcher.search(query, max_results=max_results)
    return [paper.to_dict() for paper in papers]

@mcp.tool()
async def search_arxiv(query: str, max_results: int = 10) -> List[Dict]:
    """Search academic papers from arXiv."""
    return await async_search(arxiv_searcher, query, max_results)
```

### CLI commands use asyncio to run async functions
```python
# In cli.py
@app.command()
def search(query: str, source: str = "arxiv", max_results: int = 10):
    """Search for papers."""
    async def run_search():
        papers = await searcher.search(query, max_results=max_results)
        display_papers(papers, source)
    
    asyncio.run(run_search())
```

### Paper object creation
```python
from datetime import datetime

paper = Paper(
    paper_id="unique-id",
    title="Paper Title",
    authors=["Author One", "Author Two"],
    abstract="Paper abstract text",
    doi="10.1234/example.doi",
    published_date=datetime(2024, 1, 1),
    pdf_url="https://example.com/paper.pdf",
    url="https://example.com/paper",
    source="example_platform"
)
```

### Error handling in searchers

**Comprehensive Error Handling Pattern:**

```python
import httpx
from typing import List

async def search(self, query: str, max_results: int = 10) -> List[Paper]:
    """
    Search with robust error handling.
    
    Returns empty list on errors to avoid breaking the application.
    Logs errors for debugging.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                timeout=30.0,  # Always set timeout
                follow_redirects=True
            )
            response.raise_for_status()
            data = response.json()
            
    except httpx.TimeoutException:
        print(f"Timeout while searching {self.__class__.__name__}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"HTTP error {e.response.status_code}: {e}")
        return []
    except httpx.RequestError as e:
        print(f"Network error: {e}")
        return []
    except ValueError as e:
        print(f"JSON parsing error: {e}")
        return []
    
    # Parse results with error handling
    papers = []
    for item in data.get('results', []):
        try:
            paper = self._parse_paper(item)
            papers.append(paper)
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error parsing paper: {e}")
            continue  # Skip malformed papers
    
    return papers

def _parse_paper(self, item: dict) -> Paper:
    """Helper to parse single paper with validation."""
    # Validate required fields
    if not item.get('id'):
        raise ValueError("Missing paper ID")
    
    # Use get() with defaults for optional fields
    return Paper(
        paper_id=str(item['id']),
        title=item.get('title', 'Untitled'),
        authors=item.get('authors', []),
        abstract=item.get('abstract', ''),
        doi=item.get('doi', ''),
        published_date=self._parse_date(item.get('date')),
        pdf_url=item.get('pdf_url', ''),
        url=item.get('url', ''),
        source=self.source_name
    )
```

---

## Best Practices

### 1. Type Hints
Always use type hints for better IDE support and error detection:
```python
from typing import List, Optional, Dict
from datetime import datetime

async def search(self, query: str, max_results: int = 10) -> List[Paper]:
    """Type hints make code self-documenting."""
    pass
```

### 2. Async Everywhere
All network operations must be async:
```python
# ✅ Good
async def search(self, query: str) -> List[Paper]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
# ❌ Bad  
def search(self, query: str) -> List[Paper]:
    response = requests.get(url)  # Blocks async event loop
```

### 3. Context Managers
Always use context managers for resources:
```python
# ✅ Good - auto-closes connection
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# ❌ Bad - may leak connections
client = httpx.AsyncClient()
response = await client.get(url)
```

### 4. Timeouts
Always set timeouts to prevent hanging:
```python
# ✅ Good
response = await client.get(url, timeout=30.0)

# ❌ Bad - infinite wait
response = await client.get(url)
```

### 5. Error Recovery
Return empty results rather than crashing:
```python
# ✅ Good
try:
    papers = await searcher.search(query)
except Exception as e:
    print(f"Error: {e}")
    return []  # Graceful degradation

# ❌ Bad - crashes entire application
papers = await searcher.search(query)  # No error handling
```

### 6. Validation
Validate inputs and API responses:
```python
# ✅ Good
if not query or not query.strip():
    return []

if max_results < 1 or max_results > 100:
    max_results = 10  # Sensible default

# Validate API response structure
if not isinstance(data, dict) or 'results' not in data:
    return []
```

### 7. Documentation
Document complex logic and API quirks:
```python
async def search(self, query: str, max_results: int = 10) -> List[Paper]:
    """
    Search for papers.
    
    Args:
        query: Search query. Platform supports Boolean operators (AND, OR, NOT).
        max_results: Max results (1-100). API paginates at 100.
    
    Returns:
        List of Paper objects. Returns empty list on errors.
    
    Notes:
        - API rate limit: 100 requests/minute
        - Some papers may lack PDFs
        - Date format varies by platform (ISO 8601 preferred)
    
    Examples:
        >>> papers = await searcher.search("quantum computing", max_results=5)
        >>> print(f"Found {len(papers)} papers")
    """
```

### 8. Testing
Test both success and failure cases:
```python
def test_search_success(self):
    """Test normal search operation."""
    papers = asyncio.run(searcher.search("test", max_results=5))
    self.assertIsInstance(papers, list)
    self.assertLessEqual(len(papers), 5)

def test_search_empty_query(self):
    """Test handling of empty query."""
    papers = asyncio.run(searcher.search("", max_results=5))
    self.assertEqual(papers, [])

def test_search_network_error(self):
    """Test handling of network errors."""
    # Should not crash, should return empty list
    searcher.base_url = "http://invalid.invalid"
    papers = asyncio.run(searcher.search("test"))
    self.assertEqual(papers, [])
```

---

## Common Pitfalls

### ❌ Don't: Block the Event Loop
```python
# BAD - blocks async
def search(self, query: str):
    time.sleep(1)  # Blocks everything
    return requests.get(url)  # Synchronous
```

### ✅ Do: Use Async Properly
```python
# GOOD - non-blocking
async def search(self, query: str):
    await asyncio.sleep(1)  # Yields control
    async with httpx.AsyncClient() as client:
        return await client.get(url)
```

### ❌ Don't: Ignore Errors Silently
```python
# BAD - swallows all errors
try:
    papers = await searcher.search(query)
except:
    pass  # User has no idea what went wrong
```

### ✅ Do: Log and Handle Gracefully
```python
# GOOD - informs user, degrades gracefully
try:
    papers = await searcher.search(query)
except httpx.HTTPError as e:
    print(f"Search failed: {e}")
    return []
```

### ❌ Don't: Assume API Structure
```python
# BAD - crashes if structure changes
paper_id = data['results'][0]['id']
```

### ✅ Do: Validate Structure
```python
# GOOD - handles missing data
results = data.get('results', [])
if results:
    paper_id = results[0].get('id', 'unknown')
```

---

## Documentation

- Update README.md when adding new features or platforms
- Keep the TODO list in README.md up to date
- Document any new environment variables in README.md
- Add docstrings to all public methods and classes

## MCP Integration Notes

- This server uses the FastMCP framework from the MCP Python SDK
- Tools are registered using `@mcp.tool()` decorator
- All tool functions should be async
- Tool docstrings are exposed to MCP clients as tool descriptions
- Return types should be JSON-serializable (Dict, List, str, etc.)

## Dependencies

When adding new dependencies:
1. Add them to `dependencies` in `pyproject.toml`
2. Run `uv add <package>` to update lock file
3. Document why the dependency is needed
4. Prefer lightweight, well-maintained packages

**Current key dependencies:**
- `httpx[socks]>=0.28.1` - Async HTTP client for all network requests
- `fastmcp` - FastMCP framework for MCP server
- `mcp[cli]>=1.6.0` - MCP Python SDK
- `typer>=0.9.0` - CLI framework
- `rich>=13.0.0` - Enhanced terminal output
- `feedparser` - RSS/Atom feed parsing (for arXiv)
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML/HTML parser
- `PyPDF2>=3.0.0` - PDF text extraction

## Version Management

- Version is defined in `pyproject.toml`
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version before creating release tags
- Tag format: `v0.1.0`, `v0.2.0`, etc.
