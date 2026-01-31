import os
import json
import logging
import time
import threading
import numpy as np
from typing import List, Dict, Optional

import faiss

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("rag_service")

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_DIR = os.path.join(BASE_DIR, "ai")
DATA_DIR = os.path.join(BASE_DIR, "data")

FAISS_INDEX_PATH = os.path.join(AI_DIR, "index.faiss")
CHUNKS_PATH = os.path.join(DATA_DIR, "medical_final_dataset.json")
EMBEDDINGS_PATH = os.path.join(AI_DIR, "embeddings.npy")

# =========================================================
# GLOBAL STATE
# =========================================================

_embedding_model = None
_faiss_index = None
_chunks: List[Dict] = []
_initialized = False
_model_lock = threading.Lock()  # Thread lock for model loading


# =========================================================
# EMBEDDING MODEL (all-MiniLM-L6-v2)
# =========================================================

def get_embedding_model():
    """Load or return cached SentenceTransformer model (thread-safe)"""
    global _embedding_model
    
    if _embedding_model is not None:
        return _embedding_model
    
    with _model_lock:
        # Double-check after acquiring lock
        if _embedding_model is not None:
            return _embedding_model
        
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info("Loading all-MiniLM-L6-v2 embedding model...")
            start = time.time()
            
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            
            logger.info(f"Embedding model loaded in {time.time() - start:.2f}s")
            return _embedding_model
            
        except ImportError:
            logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
            raise RuntimeError("sentence-transformers package required")


# =========================================================
# FAISS INDEX & CHUNKS LOADING
# =========================================================

_index_lock = threading.Lock()  # Thread lock for index loading

def load_rag_index():
    """Load FAISS index and chunks from disk (thread-safe)"""
    global _faiss_index, _chunks, _initialized
    
    if _initialized:
        return True
    
    with _index_lock:
        # Double-check after acquiring lock
        if _initialized:
            return True
        
        try:
            # Check if files exist
            if not os.path.exists(FAISS_INDEX_PATH):
                logger.warning(f"FAISS index not found at {FAISS_INDEX_PATH}")
                logger.info("RAG will need to be rebuilt. Run rebuild_rag_index()")
                return False
            
            if not os.path.exists(CHUNKS_PATH):
                logger.warning(f"Chunks file not found at {CHUNKS_PATH}")
                return False
            
            logger.info("Loading FAISS index and chunks...")
            start = time.time()
            
            # Load FAISS index
            _faiss_index = faiss.read_index(FAISS_INDEX_PATH)
            logger.info(f"FAISS index loaded: {_faiss_index.ntotal} vectors")
            
            # Load chunks
            with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                _chunks = json.load(f)
            logger.info(f"Loaded {len(_chunks)} text chunks")
            
            _initialized = True
            logger.info(f"RAG system initialized in {time.time() - start:.2f}s")
            
            return True
            
        except Exception as e:
            logger.exception(f"Failed to load RAG index: {e}")
            return False


# =========================================================
# REBUILD INDEX (run this if embeddings need updating)
# =========================================================

def rebuild_rag_index(chunks: List[Dict] = None):
    """Rebuild FAISS index from chunks using MiniLM embeddings"""
    global _faiss_index, _chunks, _initialized
    
    logger.info("Rebuilding RAG index with MiniLM embeddings...")
    start = time.time()
    
    # Load existing chunks if not provided
    if chunks is None:
        if os.path.exists(CHUNKS_PATH):
            with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            logger.info(f"Loaded {len(chunks)} existing chunks")
        else:
            logger.error("No chunks provided and no medical_final_dataset.json found")
            return False
    
    if not chunks:
        logger.error("No chunks to index")
        return False
    
    # Get embedding model
    model = get_embedding_model()
    
    # Extract texts
    texts = [c["text"] if isinstance(c, dict) else c for c in chunks]
    
    # Generate embeddings
    logger.info(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True,  # For cosine similarity
        convert_to_numpy=True
    ).astype("float32")
    
    logger.info(f"Embeddings shape: {embeddings.shape}")
    
    # Create FAISS index (Inner Product = cosine similarity for normalized vectors)
    dimension = embeddings.shape[1]
    _faiss_index = faiss.IndexFlatIP(dimension)
    _faiss_index.add(embeddings)
    
    logger.info(f"FAISS index created with {_faiss_index.ntotal} vectors")
    
    # Save to disk
    os.makedirs(AI_DIR, exist_ok=True)
    
    faiss.write_index(_faiss_index, FAISS_INDEX_PATH)
    logger.info(f"FAISS index saved to {FAISS_INDEX_PATH}")
    
    np.save(EMBEDDINGS_PATH, embeddings)
    logger.info(f"Embeddings saved to {EMBEDDINGS_PATH}")
    
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    logger.info(f"Chunks saved to {CHUNKS_PATH}")
    
    _chunks = chunks
    _initialized = True
    
    logger.info(f"RAG index rebuilt in {time.time() - start:.2f}s")
    return True


# =========================================================
# SEMANTIC SEARCH
# =========================================================

def search_similar(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.3
) -> List[Dict]:
    """
    Search for similar chunks using semantic similarity.
    
    Args:
        query: The search query
        top_k: Number of results to return
        score_threshold: Minimum similarity score (0-1)
    
    Returns:
        List of dicts with 'text', 'score', and 'metadata'
    """
    global _faiss_index, _chunks
    
    # Ensure index is loaded
    if not _initialized:
        if not load_rag_index():
            logger.warning("RAG index not available")
            return []
    
    if _faiss_index is None or not _chunks:
        logger.warning("RAG index or chunks not loaded")
        return []
    
    try:
        model = get_embedding_model()
        
        # Encode query
        query_embedding = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")
        
        # Search FAISS
        scores, indices = _faiss_index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(_chunks):
                continue
            
            if score < score_threshold:
                continue
            
            chunk = _chunks[idx]
            results.append({
                "text": chunk["text"] if isinstance(chunk, dict) else chunk,
                "score": float(score),
                "metadata": chunk.get("metadata", {}) if isinstance(chunk, dict) else {}
            })
        
        return results
        
    except Exception as e:
        logger.exception(f"Search failed: {e}")
        return []


# =========================================================
# CONTEXT BUILDER FOR LLM
# =========================================================

def build_rag_context(
    query: str,
    top_k: int = 3,
    max_context_length: int = 1500
) -> str:
    """
    Build context string from RAG results for LLM prompt.
    
    Args:
        query: User's question
        top_k: Number of chunks to retrieve
        max_context_length: Maximum characters for context
    
    Returns:
        Formatted context string
    """
    results = search_similar(query, top_k=top_k)
    
    if not results:
        return ""
    
    context_parts = []
    total_length = 0
    
    for i, result in enumerate(results, 1):
        text = result["text"].strip()
        
        # Check if adding this would exceed limit
        if total_length + len(text) > max_context_length:
            # Truncate this chunk to fit
            remaining = max_context_length - total_length
            if remaining > 100:  # Only add if meaningful length remains
                text = text[:remaining] + "..."
            else:
                break
        
        context_parts.append(f"[Source {i}]: {text}")
        total_length += len(text)
    
    return "\n\n".join(context_parts)


# =========================================================
# INITIALIZATION
# =========================================================

def init_rag():
    """Initialize RAG system on startup"""
    logger.info("Initializing RAG system...")
    
    # Try to load existing index
    if load_rag_index():
        # Also preload embedding model
        try:
            get_embedding_model()
            logger.info("RAG system ready!")
            return True
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            return False
    
    logger.warning("RAG index not found. System will work without RAG context.")
    return False


# =========================================================
# CLI TESTING
# =========================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rebuild":
        print("Rebuilding RAG index...")
        rebuild_rag_index()
    else:
        # Initialize
        init_rag()
        
        # Interactive search
        print("\n=== RAG Search Test ===")
        print("Enter a medical question (or 'quit' to exit):\n")
        
        while True:
            query = input("Query: ").strip()
            if not query or query.lower() == "quit":
                break
            
            print("\n--- Search Results ---")
            results = search_similar(query, top_k=3)
            
            if not results:
                print("No results found.\n")
                continue
            
            for i, r in enumerate(results, 1):
                print(f"\n[{i}] Score: {r['score']:.3f}")
                print(f"    {r['text'][:200]}...")
            
            print("\n--- RAG Context ---")
            context = build_rag_context(query)
            print(context[:500] + "..." if len(context) > 500 else context)
            print()
