import os
import json
import time
import logging
from enum import Enum
from typing import List, Dict, Optional

from groq import Groq

# Import RAG service (handle both module and standalone execution)
try:
    from services.rag_service import build_rag_context, init_rag
except ImportError:
    from rag_service import build_rag_context, init_rag

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("medchat")

# =========================================================
# RAG CONFIG
# =========================================================
USE_RAG = os.getenv("USE_RAG", "true").lower() == "true"
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
RAG_MAX_CONTEXT = int(os.getenv("RAG_MAX_CONTEXT", "1500"))

# =========================================================
# GROQ CONFIG (FREE API - 30 req/min, 6000 req/day)
# =========================================================
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Free, fast, powerful

_client: Optional[Groq] = None


def get_groq_client() -> Groq:
    """Get or create Groq client"""
    global _client
    
    if _client:
        return _client
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("❌ GROQ_API_KEY not found. Get free key at https://console.groq.com/keys")
    
    logger.info(f"Initializing Groq client with model: {GROQ_MODEL}")
    _client = Groq(api_key=api_key)
    return _client


# =========================================================
# INTENT DEFINITIONS
# =========================================================

class Intent(str, Enum):
    MEDICAL = "medical"
    GREETING = "greeting"
    THANKS = "thanks"
    GOODBYE = "goodbye"
    IDENTITY = "identity"
    REJECT = "reject"


# =========================================================
# INTENT DETECTION (CLEAN & PREDICTABLE)
# =========================================================

def detect_intent(question: str) -> Intent:
    q = question.lower().strip()

    greetings = ("hi", "hello", "hey", "good morning", "good evening")
    thanks = ("thanks", "thank you", "appreciate")
    goodbye = ("bye", "goodbye", "see you", "take care")
    identity = (
        "who are you", "what is medchat", "are you a doctor",
        "what can you do", "your purpose"
    )

    if q.startswith(greetings):
        return Intent.GREETING
    if any(t in q for t in thanks):
        return Intent.THANKS
    if any(b in q for b in goodbye):
        return Intent.GOODBYE
    if any(i in q for i in identity):
        return Intent.IDENTITY

    # Comprehensive medical triggers - diseases, symptoms, treatments, body parts
    medical_triggers = (
        # Symptoms
        "pain", "symptom", "ache", "fever", "headache", "dizziness",
        "vomiting", "nausea", "fatigue", "tired", "weakness", "cough",
        "cold", "flu", "sore throat", "rash", "swelling", "bleeding",
        "numbness", "tingling", "cramp", "spasm", "itch", "burn",
        # Diseases & Conditions
        "diabetes", "hypertension", "cancer", "asthma", "allergy",
        "arthritis", "migraine", "stroke", "heart attack", "covid",
        "pneumonia", "bronchitis", "anemia", "thyroid", "cholesterol",
        "obesity", "insomnia", "alzheimer", "parkinson", "epilepsy",
        "hepatitis", "kidney", "liver", "ulcer", "hernia", "tumor",
        # Mental Health
        "anxiety", "depression", "stress", "mental", "psychiatric",
        "bipolar", "schizophrenia", "adhd", "autism", "panic",
        # Body Parts
        "heart", "lung", "brain", "stomach", "intestine", "bone",
        "muscle", "nerve", "blood", "skin", "eye", "ear", "nose",
        "throat", "chest", "back", "neck", "arm", "leg", "joint",
        # Medical Terms
        "treatment", "medicine", "drug", "pill", "tablet", "injection",
        "vaccine", "surgery", "therapy", "diagnosis", "prescription",
        "doctor", "hospital", "clinic", "emergency", "ambulance",
        "blood pressure", "blood sugar", "infection", "virus", "bacteria",
        "antibiotic", "painkiller", "dosage", "side effect", "overdose",
        # Question patterns for medical info
        "what is", "what are", "how to treat", "how to cure", "cause of",
        "causes of", "prevention", "prevent", "remedy", "remedies",
        "home treatment", "first aid", "healthy", "health", "medical",
        "disease", "disorder", "condition", "syndrome", "chronic"
    )

    if any(m in q for m in medical_triggers):
        return Intent.MEDICAL

    # If it looks like a question about something, default to medical (be more permissive)
    if q.endswith("?") and len(q.split()) >= 3:
        return Intent.MEDICAL

    return Intent.REJECT


# =========================================================
# STATIC RESPONSES
# =========================================================

def get_static_response(intent: Intent) -> str:
    responses = {
        Intent.GREETING: (
            "**Hello! 👋 Welcome to MedChat AI**\n\n"
            "I'm your medical information assistant. I can help you with:\n\n"
            "• Understanding symptoms and conditions\n"
            "• General health information\n"
            "• Treatment overviews\n\n"
            "How can I assist you today?"
        ),
        Intent.THANKS: (
            "**You're welcome! 😊**\n\n"
            "I'm glad I could help. Feel free to ask if you have more health questions.\n\n"
            "*Stay healthy!*"
        ),
        Intent.GOODBYE: (
            "**Goodbye! 👋 Take care!**\n\n"
            "Remember to consult a healthcare professional for any urgent concerns.\n\n"
            "*Wishing you good health!*"
        ),
        Intent.IDENTITY: (
            "**About MedChat AI**\n\n"
            "I'm an AI-powered medical information assistant designed to help you understand health topics.\n\n"
            "**What I can do:**\n"
            "• Explain medical conditions and symptoms\n"
            "• Provide general health information\n"
            "• Offer wellness tips and guidance\n\n"
            "**Important:** I provide educational information only. I cannot diagnose conditions or prescribe treatments. Always consult a qualified healthcare provider for medical advice."
        ),
        Intent.REJECT: (
            "**I specialize in medical topics only**\n\n"
            "I'm designed to help with health-related questions such as:\n\n"
            "• Symptoms and conditions\n"
            "• Treatment information\n"
            "• General health advice\n\n"
            "Please ask a medical or health-related question."
        ),
    }
    return responses[intent]


# =========================================================
# SYSTEM PROMPT (PROFESSIONAL)
# =========================================================

def build_system_prompt(rag_context: str = "") -> str:
    base_prompt = (
        "You are MedChat AI, a professional medical information assistant.\n\n"
    )
    
    # Add RAG context if available
    if rag_context:
        base_prompt += (
            "REFERENCE INFORMATION:\n"
            "Use the following verified medical information to answer the user's question. "
            "Prioritize this information but supplement with your knowledge when needed.\n\n"
            f"{rag_context}\n\n"
            "---\n\n"
        )
    
    base_prompt += (
        "RESPONSE FORMAT:\n"
        "1. Start with a **bold heading** summarizing the topic\n"
        "2. Provide a brief 1-2 sentence overview\n"
        "3. Use **bold** for key terms and important points\n"
        "4. Use bullet points (•) for lists - keep to 4-6 items max\n"
        "5. Use *italics* for medical terms or emphasis\n"
        "6. Keep total response concise (150-250 words)\n\n"
        "STRUCTURE EXAMPLE:\n"
        "**Topic Name**\n\n"
        "Brief overview sentence.\n\n"
        "**Key Points:**\n"
        "• Point one with **important term**\n"
        "• Point two\n"
        "• Point three\n\n"
        "**When to See a Doctor:**\n"
        "Brief guidance.\n\n"
        "*Disclaimer: Consult a healthcare provider for personalized advice.*\n\n"
        "CONTENT RULES:\n"
        "1. Provide accurate, educational medical information\n"
        "2. Do NOT diagnose specific conditions\n"
        "3. Do NOT prescribe medications or dosages\n"
        "4. Include when to seek professional help\n"
        "5. End with a brief disclaimer when appropriate\n"
        "6. Be empathetic and professional in tone\n"
    )
    
    return base_prompt


# =========================================================
# MEDICAL ANSWER GENERATION
# =========================================================

def generate_medical_answer(
    question: str,
    history: Optional[List[Dict]] = None,
    max_tokens: int = 300,  # Reduced for shorter responses
) -> str:
    """Generate medical answer using Groq with RAG context"""
    try:
        client = get_groq_client()
        start = time.time()
        
        # Get RAG context if enabled
        rag_context = ""
        if USE_RAG:
            try:
                rag_context = build_rag_context(
                    query=question,
                    top_k=RAG_TOP_K,
                    max_context_length=RAG_MAX_CONTEXT
                )
                if rag_context:
                    logger.info(f"RAG context retrieved: {len(rag_context)} chars")
            except Exception as e:
                logger.warning(f"RAG context retrieval failed: {e}")
        
        # Build messages list with RAG-enhanced system prompt
        messages = [
            {"role": "system", "content": build_system_prompt(rag_context)}
        ]
        
        # Add history (last 3 messages)
        if history:
            for msg in history[-3:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")[:500]
                })
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        # Call Groq API
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,  # Lower temperature for more focused responses
            max_tokens=max_tokens,
        )
        
        answer = response.choices[0].message.content.strip()
        logger.info(f"Groq response generated in {time.time() - start:.2f}s (RAG: {'yes' if rag_context else 'no'})")
        return answer

    except Exception as e:
        logger.exception("Medical answer generation failed")
        return f"⚠️ Service temporarily unavailable: {str(e)}"


# =========================================================
# STREAMING (SSE-READY)
# =========================================================
def stream_medical_answer(question: str):
    """Stream medical answer using Groq with RAG context"""
    try:
        client = get_groq_client()
        
        # Get RAG context if enabled
        rag_context = ""
        if USE_RAG:
            try:
                rag_context = build_rag_context(
                    query=question,
                    top_k=RAG_TOP_K,
                    max_context_length=RAG_MAX_CONTEXT
                )
                if rag_context:
                    logger.info(f"RAG context for streaming: {len(rag_context)} chars")
            except Exception as e:
                logger.warning(f"RAG context retrieval failed: {e}")
        
        messages = [
            {"role": "system", "content": build_system_prompt(rag_context)},
            {"role": "user", "content": question}
        ]
        
        # Call Groq API with streaming
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,  # Lower temperature for more focused responses
            max_tokens=300,   # Reduced for shorter responses
            stream=True,  # Enable streaming
        )
        
        # Stream the response
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'token': token})}\n\n"
        
        yield f"data: {json.dumps({'done': True})}\n\n"

    except Exception as e:
        logger.exception("Streaming generation failed")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


# =========================================================
# MAIN ROUTER (USE THIS)
# =========================================================

def handle_question(
    question: str,
    history: Optional[List[Dict]] = None
) -> str:
    intent = detect_intent(question)

    if intent != Intent.MEDICAL:
        return get_static_response(intent)

    return generate_medical_answer(question, history)


# =========================================================
# QUICK MANUAL TEST
# =========================================================

if __name__ == "__main__":
    while True:
        q = input("\nYou: ").strip()
        if not q:
            continue
        print("\nBot:", handle_question(q))
