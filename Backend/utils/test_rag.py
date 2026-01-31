"""Test RAG Search"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag_service import init_rag, search_similar, build_rag_context

# Initialize
print('Initializing RAG...')
init_rag()

# Test search
query = 'What are the symptoms of diabetes?'
print(f'\nQuery: {query}')
print('\n--- Search Results ---')
results = search_similar(query, top_k=3)
for i, r in enumerate(results, 1):
    print(f'[{i}] Score: {r["score"]:.3f}')
    print(f'    {r["text"][:150]}...')

print('\n--- RAG Context ---')
context = build_rag_context(query)
print(context[:500] + '...' if len(context) > 500 else context)
