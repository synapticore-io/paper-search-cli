"""
Document processing module using Docling for paper-search-mcp.
Provides advanced PDF parsing, structure extraction, and text processing.
"""
import os
from typing import Dict, Optional
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("Docling not available. Install with: pip install docling")

class DocumentProcessor:
    """
    Document processor using Docling for advanced parsing.
    Handles PDFs, DOCX, PPTX, HTML, and other formats.
    """
    
    def __init__(self):
        """Initialize document processor."""
        if not DOCLING_AVAILABLE:
            raise ImportError("Docling is required for document processing")
        
        self.converter = DocumentConverter()
    
    async def process_pdf(self, pdf_path: str) -> Dict:
        """
        Process a PDF file and extract structured content.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted content and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Convert document
            result = self.converter.convert(pdf_path)
            doc = result.document
            
            # Extract structured information
            processed_data = {
                'text': doc.export_to_markdown(),
                'metadata': {
                    'title': getattr(doc, 'title', ''),
                    'num_pages': len(doc.pages) if hasattr(doc, 'pages') else 0,
                    'has_tables': len(doc.tables) > 0 if hasattr(doc, 'tables') else False,
                    'has_figures': len(doc.figures) > 0 if hasattr(doc, 'figures') else False,
                },
                'structure': {
                    'sections': self._extract_sections(doc),
                    'tables': self._extract_tables(doc),
                    'figures': self._extract_figures(doc),
                    'references': self._extract_references(doc),
                },
                'format': 'markdown'
            }
            
            return processed_data
            
        except Exception as e:
            print(f"Error processing PDF with Docling: {e}")
            # Fallback to basic text extraction
            return await self._fallback_extraction(pdf_path)
    
    def _extract_sections(self, doc) -> list:
        """Extract document sections."""
        sections = []
        try:
            if hasattr(doc, 'sections'):
                for section in doc.sections:
                    sections.append({
                        'title': getattr(section, 'title', ''),
                        'level': getattr(section, 'level', 0),
                        'content': getattr(section, 'text', '')
                    })
        except Exception as e:
            print(f"Error extracting sections: {e}")
        return sections
    
    def _extract_tables(self, doc) -> list:
        """Extract tables from document."""
        tables = []
        try:
            if hasattr(doc, 'tables'):
                for table in doc.tables:
                    tables.append({
                        'caption': getattr(table, 'caption', ''),
                        'data': getattr(table, 'data', []),
                        'page': getattr(table, 'page', 0)
                    })
        except Exception as e:
            print(f"Error extracting tables: {e}")
        return tables
    
    def _extract_figures(self, doc) -> list:
        """Extract figures from document."""
        figures = []
        try:
            if hasattr(doc, 'figures'):
                for figure in doc.figures:
                    figures.append({
                        'caption': getattr(figure, 'caption', ''),
                        'page': getattr(figure, 'page', 0)
                    })
        except Exception as e:
            print(f"Error extracting figures: {e}")
        return figures
    
    def _extract_references(self, doc) -> list:
        """Extract references/citations from document."""
        references = []
        try:
            if hasattr(doc, 'references'):
                references = [str(ref) for ref in doc.references]
        except Exception as e:
            print(f"Error extracting references: {e}")
        return references
    
    async def _fallback_extraction(self, pdf_path: str) -> Dict:
        """Fallback to basic PDF text extraction."""
        from PyPDF2 import PdfReader
        
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return {
                'text': text.strip(),
                'metadata': {
                    'title': '',
                    'num_pages': len(reader.pages),
                    'has_tables': False,
                    'has_figures': False,
                },
                'structure': {
                    'sections': [],
                    'tables': [],
                    'figures': [],
                    'references': [],
                },
                'format': 'plain_text',
                'extraction_method': 'fallback'
            }
        except Exception as e:
            print(f"Fallback extraction failed: {e}")
            return {
                'text': '',
                'metadata': {},
                'structure': {},
                'format': 'error',
                'error': str(e)
            }
    
    async def process_url(self, url: str, output_dir: str = "./downloads") -> Dict:
        """
        Process a document from URL.
        
        Args:
            url: URL to document
            output_dir: Directory to save temporary files
            
        Returns:
            Processed document data
        """
        try:
            # Docling can process URLs directly
            result = self.converter.convert(url)
            doc = result.document
            
            return {
                'text': doc.export_to_markdown(),
                'metadata': {
                    'source_url': url,
                    'title': getattr(doc, 'title', ''),
                },
                'format': 'markdown'
            }
        except Exception as e:
            print(f"Error processing URL with Docling: {e}")
            return {
                'text': '',
                'metadata': {'source_url': url},
                'format': 'error',
                'error': str(e)
            }
    
    def export_to_format(self, doc_data: Dict, format: str = 'markdown') -> str:
        """
        Export processed document to specified format.
        
        Args:
            doc_data: Processed document data
            format: Output format (markdown, html, json)
            
        Returns:
            Formatted document text
        """
        if format == 'markdown':
            return doc_data.get('text', '')
        elif format == 'html':
            # Convert markdown to HTML if needed
            return doc_data.get('text', '')
        elif format == 'json':
            import json
            return json.dumps(doc_data, indent=2)
        else:
            return doc_data.get('text', '')
