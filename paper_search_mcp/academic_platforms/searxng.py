"""
SearXNG metasearch engine integration for paper-search-mcp.
Provides privacy-focused search across multiple academic and general search engines.
"""
import os
from typing import List
from datetime import datetime
import httpx
from ..paper import Paper

class SearXNGSearcher:
    """Searcher using SearXNG metasearch engine."""
    
    def __init__(self, base_url: str = None):
        """
        Initialize SearXNG searcher.
        
        Args:
            base_url: SearXNG instance URL (default: from env SEARXNG_URL)
        """
        self.base_url = base_url or os.getenv('SEARXNG_URL', 'http://localhost:8080')
    
    async def search(self, query: str, max_results: int = 10, 
                    category: str = 'science') -> List[Paper]:
        """
        Search using SearXNG metasearch engine.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            category: Search category (general, science, files, etc.)
            
        Returns:
            List of Paper objects
        """
        params = {
            'q': query,
            'format': 'json',
            'categories': category,
            'pageno': 1
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/search",
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPError as e:
                print(f"SearXNG search error: {e}")
                return []
        
        papers = []
        results = data.get('results', [])[:max_results]
        
        for idx, item in enumerate(results):
            try:
                # Extract information from search result
                title = item.get('title', 'Untitled')
                url = item.get('url', '')
                content = item.get('content', '')
                
                # Try to extract PDF URL if available
                pdf_url = ''
                if 'pdf' in url.lower() or 'arxiv.org' in url:
                    pdf_url = url
                
                # Create paper object
                papers.append(Paper(
                    paper_id=f"searxng_{idx}_{hash(url)}",
                    title=title,
                    authors=[item.get('author', 'Unknown')],  # SearXNG may not have detailed author info
                    abstract=content[:500] if content else '',  # Use content as abstract
                    doi='',  # SearXNG doesn't always provide DOI
                    published_date=datetime.now(),  # Use current date as fallback
                    pdf_url=pdf_url,
                    url=url,
                    source='searxng',
                    keywords=item.get('tags', []),
                    extra={
                        'engine': item.get('engine', ''),
                        'score': item.get('score', 0),
                        'category': item.get('category', category)
                    }
                ))
            except Exception as e:
                print(f"Error parsing SearXNG result: {e}")
                continue
        
        return papers
    
    async def download_pdf(self, paper_id: str, save_path: str) -> str:
        """
        Download PDF - not directly supported by SearXNG.
        
        Args:
            paper_id: Paper ID
            save_path: Save directory
            
        Raises:
            NotImplementedError: SearXNG is a search aggregator, not a PDF provider
        """
        raise NotImplementedError(
            "SearXNG is a metasearch engine and doesn't directly provide PDF downloads. "
            "Use the paper's URL to access the original source."
        )
    
    async def read_paper(self, paper_id: str, save_path: str = "./downloads") -> str:
        """
        Read paper - not directly supported by SearXNG.
        
        Args:
            paper_id: Paper ID
            save_path: Save directory
            
        Raises:
            NotImplementedError: SearXNG is a search aggregator
        """
        raise NotImplementedError(
            "SearXNG is a metasearch engine and doesn't directly provide paper content. "
            "Use the paper's URL to access the original source."
        )
