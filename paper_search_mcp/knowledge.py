"""
SurrealDB knowledge graph and memory module for paper-search-mcp.
Provides knowledge synthesis, storage, and retrieval capabilities.
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
from surrealdb import Surreal

class KnowledgeStore:
    """
    Knowledge graph manager using SurrealDB.
    Stores papers, concepts, relationships, and memories.
    """
    
    def __init__(self, url: str = None, user: str = None, password: str = None,
                 namespace: str = None, database: str = None):
        """
        Initialize SurrealDB connection.
        
        Args:
            url: SurrealDB connection URL (default: from env SURREALDB_URL)
            user: Database user (default: from env SURREALDB_USER)
            password: Database password (default: from env SURREALDB_PASS)
            namespace: Database namespace (default: from env SURREALDB_NS)
            database: Database name (default: from env SURREALDB_DB)
        """
        self.url = url or os.getenv('SURREALDB_URL', 'ws://localhost:8000/rpc')
        self.user = user or os.getenv('SURREALDB_USER', 'root')
        self.password = password or os.getenv('SURREALDB_PASS', 'root')
        self.namespace = namespace or os.getenv('SURREALDB_NS', 'paper_search')
        self.database = database or os.getenv('SURREALDB_DB', 'knowledge')
        self.db = None
    
    async def connect(self):
        """Establish connection to SurrealDB."""
        if not self.db:
            self.db = Surreal(self.url)
            await self.db.signin({"username": self.user, "password": self.password})
            await self.db.use(self.namespace, self.database)
            await self._init_schema()
    
    async def _init_schema(self):
        """Initialize database schema for papers and knowledge."""
        # Define paper table
        await self.db.query("""
            DEFINE TABLE paper SCHEMAFULL;
            DEFINE FIELD paper_id ON paper TYPE string;
            DEFINE FIELD title ON paper TYPE string;
            DEFINE FIELD authors ON paper TYPE array;
            DEFINE FIELD abstract ON paper TYPE string;
            DEFINE FIELD doi ON paper TYPE string;
            DEFINE FIELD published_date ON paper TYPE datetime;
            DEFINE FIELD source ON paper TYPE string;
            DEFINE FIELD url ON paper TYPE string;
            DEFINE FIELD pdf_url ON paper TYPE string;
            DEFINE FIELD categories ON paper TYPE array;
            DEFINE FIELD keywords ON paper TYPE array;
            DEFINE FIELD stored_at ON paper TYPE datetime;
            DEFINE INDEX paper_id_idx ON paper FIELDS paper_id UNIQUE;
        """)
        
        # Define concept table for extracted knowledge
        await self.db.query("""
            DEFINE TABLE concept SCHEMAFULL;
            DEFINE FIELD name ON concept TYPE string;
            DEFINE FIELD description ON concept TYPE string;
            DEFINE FIELD category ON concept TYPE string;
            DEFINE FIELD frequency ON concept TYPE int DEFAULT 1;
            DEFINE FIELD created_at ON concept TYPE datetime;
            DEFINE INDEX concept_name_idx ON concept FIELDS name UNIQUE;
        """)
        
        # Define relationship edges
        await self.db.query("""
            DEFINE TABLE relates_to SCHEMAFULL TYPE RELATION;
            DEFINE FIELD in ON relates_to TYPE record;
            DEFINE FIELD out ON relates_to TYPE record;
            DEFINE FIELD relationship_type ON relates_to TYPE string;
            DEFINE FIELD strength ON relates_to TYPE float DEFAULT 1.0;
            DEFINE FIELD created_at ON relates_to TYPE datetime;
        """)
    
    async def store_paper(self, paper_data: Dict) -> str:
        """
        Store a paper in the knowledge graph.
        
        Args:
            paper_data: Dictionary with paper information
            
        Returns:
            Record ID of stored paper
        """
        await self.connect()
        
        # Add storage timestamp
        paper_data['stored_at'] = datetime.utcnow().isoformat()
        
        # Store paper
        result = await self.db.create('paper', paper_data)
        return result[0]['id'] if result else None
    
    async def get_paper(self, paper_id: str) -> Optional[Dict]:
        """
        Retrieve a paper by its ID.
        
        Args:
            paper_id: Unique paper identifier
            
        Returns:
            Paper data or None if not found
        """
        await self.connect()
        
        result = await self.db.query(
            "SELECT * FROM paper WHERE paper_id = $paper_id LIMIT 1",
            {"paper_id": paper_id}
        )
        return result[0] if result and len(result) > 0 else None
    
    async def search_papers(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search papers by keywords in title or abstract.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching papers
        """
        await self.connect()
        
        result = await self.db.query("""
            SELECT * FROM paper 
            WHERE title CONTAINS $query OR abstract CONTAINS $query
            ORDER BY stored_at DESC
            LIMIT $limit
        """, {"query": query, "limit": limit})
        
        return result if result else []
    
    async def add_concept(self, name: str, description: str, category: str = "general") -> str:
        """
        Add or update a concept in the knowledge graph.
        
        Args:
            name: Concept name
            description: Concept description
            category: Concept category
            
        Returns:
            Record ID of the concept
        """
        await self.connect()
        
        # Check if concept exists
        existing = await self.db.query(
            "SELECT * FROM concept WHERE name = $name LIMIT 1",
            {"name": name}
        )
        
        if existing and len(existing) > 0:
            # Update frequency
            await self.db.query(
                "UPDATE concept SET frequency = frequency + 1 WHERE name = $name",
                {"name": name}
            )
            return existing[0]['id']
        else:
            # Create new concept
            result = await self.db.create('concept', {
                'name': name,
                'description': description,
                'category': category,
                'frequency': 1,
                'created_at': datetime.utcnow().isoformat()
            })
            return result[0]['id'] if result else None
    
    async def relate_paper_to_concept(self, paper_id: str, concept_name: str, 
                                     strength: float = 1.0) -> str:
        """
        Create relationship between paper and concept.
        
        Args:
            paper_id: Paper record ID
            concept_name: Concept name
            strength: Relationship strength (0-1)
            
        Returns:
            Relationship record ID
        """
        await self.connect()
        
        result = await self.db.query("""
            RELATE $paper_id->relates_to->concept:⟨$concept_name⟩
            SET relationship_type = 'discusses',
                strength = $strength,
                created_at = $now
        """, {
            "paper_id": paper_id,
            "concept_name": concept_name,
            "strength": strength,
            "now": datetime.utcnow().isoformat()
        })
        
        return result[0]['id'] if result and len(result) > 0 else None
    
    async def get_related_concepts(self, paper_id: str) -> List[Dict]:
        """
        Get all concepts related to a paper.
        
        Args:
            paper_id: Paper record ID
            
        Returns:
            List of related concepts with relationship data
        """
        await self.connect()
        
        result = await self.db.query("""
            SELECT ->relates_to->concept.* AS concept,
                   ->relates_to.strength AS strength
            FROM $paper_id
        """, {"paper_id": paper_id})
        
        return result if result else []
    
    async def get_similar_papers(self, paper_id: str, limit: int = 5) -> List[Dict]:
        """
        Find papers similar to the given paper based on shared concepts.
        
        Args:
            paper_id: Paper record ID
            limit: Maximum results
            
        Returns:
            List of similar papers
        """
        await self.connect()
        
        result = await self.db.query("""
            SELECT id, paper_id, title, COUNT() AS shared_concepts
            FROM (
                SELECT ->relates_to->concept<-relates_to<-paper.* AS related_papers
                FROM $paper_id
            )
            WHERE id != $paper_id
            GROUP BY id, paper_id, title
            ORDER BY shared_concepts DESC
            LIMIT $limit
        """, {"paper_id": paper_id, "limit": limit})
        
        return result if result else []
    
    async def get_knowledge_stats(self) -> Dict:
        """
        Get statistics about the knowledge graph.
        
        Returns:
            Dictionary with counts and statistics
        """
        await self.connect()
        
        papers_count = await self.db.query("SELECT COUNT() FROM paper")
        concepts_count = await self.db.query("SELECT COUNT() FROM concept")
        relations_count = await self.db.query("SELECT COUNT() FROM relates_to")
        
        return {
            "papers": papers_count[0]['count'] if papers_count else 0,
            "concepts": concepts_count[0]['count'] if concepts_count else 0,
            "relationships": relations_count[0]['count'] if relations_count else 0
        }
    
    async def close(self):
        """Close database connection."""
        if self.db:
            await self.db.close()
            self.db = None
