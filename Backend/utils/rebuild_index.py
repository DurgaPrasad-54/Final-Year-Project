"""
Rebuild RAG Index with MiniLM Embeddings

This script rebuilds the FAISS index using all-MiniLM-L6-v2 embeddings.
Run this once to convert from BioBERT to MiniLM embeddings.

Usage:
    python rebuild_index.py
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag_service import rebuild_rag_index, AI_DIR, CHUNKS_PATH


def main():
    print("=" * 60)
    print("RAG Index Rebuild with MiniLM Embeddings")
    print("=" * 60)
    
    # Check if chunks exist
    if not os.path.exists(CHUNKS_PATH):
        print(f"\n❌ Error: chunks.json not found at {CHUNKS_PATH}")
        print("Please ensure you have run the preprocessing and training notebooks first.")
        return False
    
    print(f"\n📂 AI Directory: {AI_DIR}")
    print(f"📄 Chunks Path: {CHUNKS_PATH}")
    
    # Confirm with user
    print("\n⚠️  This will rebuild the FAISS index using all-MiniLM-L6-v2 embeddings.")
    print("   The existing index.faiss and embeddings.npy will be overwritten.")
    
    response = input("\nProceed? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return False
    
    print("\n🔄 Starting rebuild...")
    success = rebuild_rag_index()
    
    if success:
        print("\n✅ RAG index rebuilt successfully!")
        print("\nFiles updated:")
        print(f"  - {os.path.join(AI_DIR, 'index.faiss')}")
        print(f"  - {os.path.join(AI_DIR, 'embeddings.npy')}")
        print(f"  - {CHUNKS_PATH}")
        print("\nYou can now restart the backend server to use the new index.")
    else:
        print("\n❌ Failed to rebuild index. Check the logs above for errors.")
    
    return success


if __name__ == "__main__":
    main()
