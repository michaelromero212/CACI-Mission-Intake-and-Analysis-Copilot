"""
RAG (Retrieval-Augmented Generation) service.

Implements simple, explainable RAG:
- Text chunking
- Embeddings via sentence-transformers (local)
- FAISS for vector storage and retrieval
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# FAISS index storage
FAISS_INDEX_PATH = Path(__file__).parent.parent / "faiss_index"


class RAGService:
    """
    Lightweight RAG implementation.
    
    - Chunks text into manageable pieces
    - Generates embeddings using sentence-transformers
    - Stores/retrieves using FAISS
    """
    
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.chunks: List[Dict[str, Any]] = []
        self._initialized = False
        
    def _initialize(self):
        """Lazy initialization of heavy dependencies."""
        if self._initialized:
            return
            
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            
            # Initialize empty FAISS index
            embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(embedding_dim)
            
            self._initialized = True
            logger.info("RAG service initialized successfully")
            
        except ImportError as e:
            logger.warning(f"RAG dependencies not available: {e}")
            self._initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            self._initialized = False
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks for processing.
        
        Args:
            text: Text to chunk
            chunk_size: Target characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        
        # Split on sentence boundaries when possible
        sentences = text.replace('\n', ' ').split('. ')
        
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append({
                        "id": chunk_id,
                        "text": current_chunk.strip(),
                        "char_count": len(current_chunk)
                    })
                    chunk_id += 1
                    
                    # Keep overlap from end of previous chunk
                    if overlap > 0:
                        words = current_chunk.split()
                        overlap_words = words[-overlap//5:] if len(words) > overlap//5 else []
                        current_chunk = " ".join(overlap_words) + " " + sentence + ". "
                    else:
                        current_chunk = sentence + ". "
                else:
                    current_chunk = sentence + ". "
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "id": chunk_id,
                "text": current_chunk.strip(),
                "char_count": len(current_chunk)
            })
        
        return chunks
    
    def add_document(self, text: str, document_id: str = None) -> int:
        """
        Add a document to the RAG index.
        
        Returns number of chunks added.
        """
        self._initialize()
        
        if not self._initialized:
            logger.warning("RAG not initialized, skipping document indexing")
            return 0
        
        chunks = self.chunk_text(text)
        
        if not chunks:
            return 0
        
        # Generate embeddings
        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_model.encode(texts)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store chunk references
        for i, chunk in enumerate(chunks):
            chunk["document_id"] = document_id
            self.chunks.append(chunk)
        
        logger.info(f"Added {len(chunks)} chunks to RAG index")
        return len(chunks)
    
    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with scores
        """
        self._initialize()
        
        if not self._initialized or not self.chunks:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search FAISS
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'),
            min(top_k, len(self.chunks))
        )
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["score"] = float(distances[0][i])
                results.append(chunk)
        
        return results
    
    def get_context_for_analysis(
        self,
        content: str,
        max_context_chars: int = 1000
    ) -> str:
        """
        Get relevant context for analyzing new content.
        
        This adds the content to the index and retrieves related context.
        """
        # Add content to index
        self.add_document(content)
        
        # Create query from first part of content
        query = content[:500]
        
        # Retrieve related chunks
        results = self.retrieve(query, top_k=3)
        
        # Combine into context string
        context_parts = []
        total_chars = 0
        
        for result in results:
            if total_chars + result["char_count"] > max_context_chars:
                break
            context_parts.append(result["text"])
            total_chars += result["char_count"]
        
        return "\n\n".join(context_parts)
    
    def clear(self):
        """Clear the RAG index."""
        if self._initialized and self.index:
            self.index.reset()
        self.chunks = []


# Global RAG service instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create the RAG service singleton."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
