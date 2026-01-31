"""Test Full Chat Integration with RAG"""
import sys
import os

# Set environment variable
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag_service import init_rag
from services.medchat_gemini import handle_question

# Initialize RAG first
print("=" * 60)
print("Testing Full Chat Integration with RAG")
print("=" * 60)

print("\n[1] Initializing RAG system...")
init_rag()

# Test questions
test_questions = [
    "What are the symptoms of diabetes?",
    "How is hypertension treated?",
    "What causes headaches?",
]

print("\n[2] Testing questions with RAG context...\n")

for q in test_questions:
    print(f"Q: {q}")
    print("-" * 40)
    answer = handle_question(q)
    # Print first 300 chars
    print(f"A: {answer[:300]}..." if len(answer) > 300 else f"A: {answer}")
    print("\n")
