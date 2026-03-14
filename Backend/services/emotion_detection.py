"""
Emotion detection using keyword-based approach (no external libraries)
Detects: happy, sad, angry, anxious, neutral
"""

import re
from enum import Enum


class Emotion(Enum):
    """Emotion types"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    NEUTRAL = "neutral"


# Emotion keyword dictionaries with weights
EMOTION_KEYWORDS = {
    "happy": {
        "keywords": [
            "happy", "glad", "joy", "joyful", "wonderful", "excellent", "amazing",
            "great", "good", "fantastic", "awesome", "excited", "excited", "delighted",
            "love", "loveit", "perfect", "brilliant", "superb", "marvelous", "blessed",
            "grateful", "thankful", "smile", "laughing", "laugh", "lol", "haha", "hehe",
            "cheerful", "content", "pleased", "thrilled", "elated", "ecstatic", "blissful",
            "wonderful", "terrific", "nice", "lovely", "beautiful", "sweet", "kind",
            "grateful", "appreciate", "blessed"
        ],
        "intensifiers": ["very", "so", "really", "extremely", "incredibly", "absolutely"],
        "base_score": 1.0
    },
    "sad": {
        "keywords": [
            "sad", "sadness", "depressed", "depression", "unhappy", "miserable", "terrible",
            "awful", "horrible", "bad", "worst", "pain", "hurt", "suffering", "suffer",
            "alone", "lonely", "loneliness", "cry", "crying", "tears", "broken", "sick",
            "tired", "exhausted", "stress", "stressed", "upset", "down", "downhearted", "distressed",
            "grieving", "grief", "mourning", "loss", "lost", "helpless", "hopeless",
            "disappointed", "disappointing", "regret", "regrets", "ashamed", "shame",
            "defeated", "weak", "frail", "desperate", "despair", "anguish"
        ],
        "intensifiers": ["very", "so", "really", "extremely", "incredibly", "absolutely"],
        "base_score": 1.0
    },
    "angry": {
        "keywords": [
            "angry", "anger", "rage", "furious", "furious", "mad", "madness", "hate",
            "hatred", "irritated", "irritable", "annoyed", "aggravated", "frustrated",
            "frustrated", "frustrating", "upset", "furious", "enraged", "infuriated",
            "disgusted", "disgusting", "disgusting", "offensive", "offended",
            "bitter", "bitter", "resentful", "resentment", "hostile", "aggressive",
            "violent", "fierce", "harsh", "terrible", "awful", "horrible",
            "unacceptable", "unacceptable", "wrong", "unfair", "unjust", "betrayed"
        ],
        "intensifiers": ["very", "so", "really", "extremely", "incredibly", "absolutely"],
        "base_score": 1.0
    },
    "anxious": {
        "keywords": [
            "anxious", "anxiety", "nervous", "nervous", "worried", "worry", "concern",
            "concerned", "fear", "afraid", "scared", "frightened", "terrified",
            "panic", "panicked", "panicking", "urgent", "urgent", "emergency",
            "desperate", "desperation", "desperate", "worried", "distressed",
            "stressed", "stress", "tense", "tension", "worried", "nervous",
            "apprehensive", "apprehension", "dread", "dreading", "horror", "horrified",
            "troubled", "trouble", "uneasy", "uneasy", "restless", "unsettled",
            "concerned", "alarmed", "alarming", "warning", "warn", "dangerous"
        ],
        "intensifiers": ["very", "so", "really", "extremely", "incredibly", "absolutely"],
        "base_score": 1.0
    }
}


def normalize_text(text):
    """Normalize text for emotion detection"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text


def count_emotion_words(text, emotion):
    """Count how many emotion keywords appear in text"""
    normalized = normalize_text(text)
    words = normalized.split()
    
    emotions_def = EMOTION_KEYWORDS.get(emotion, {})
    keywords = emotions_def.get("keywords", [])
    
    count = 0
    for word in words:
        if word in keywords:
            count += 1
    
    return count


def detect_emotion(text):
    """
    Detect emotion from text using keyword matching
    Returns (emotion, confidence)
    """
    if not text or not isinstance(text, str):
        return Emotion.NEUTRAL, 0.0
    
    normalized = normalize_text(text)
    words = set(normalized.split())
    
    emotion_scores = {
        "happy": 0,
        "sad": 0,
        "angry": 0,
        "anxious": 0
    }
    
    # Count occurrences of each emotion keyword
    for emotion_name in emotion_scores:
        keywords = EMOTION_KEYWORDS[emotion_name]["keywords"]
        for word in words:
            if word in keywords:
                emotion_scores[emotion_name] += 1
    
    # Check for intensifiers before emotion words
    intensifier_patterns = [
        r'\b(very|so|really|extremely|incredibly|absolutely)\s+\w*(happy|glad|sad|angry|fear|anxious|worried)',
    ]
    
    for pattern in intensifier_patterns:
        matches = re.findall(pattern, normalized)
        if matches:
            # Boost the score for intensified emotions
            for match in matches:
                if "happy" in match:
                    emotion_scores["happy"] += 1
                if "sad" in match:
                    emotion_scores["sad"] += 1
                if "angry" in match:
                    emotion_scores["angry"] += 1
                if "anxiety" in match or "afraid" in match or "worried" in match:
                    emotion_scores["anxious"] += 1
    
    # Find the emotion with the highest score
    max_score = max(emotion_scores.values())
    
    if max_score == 0:
        return Emotion.NEUTRAL, 0.0
    
    # Calculate confidence (0 to 1)
    text_length = len(words)
    confidence = min(1.0, max_score / max(text_length / 3, 1))  # Normalize by text length
    
    # Get the emotion with max score
    detected_emotion = max(emotion_scores, key=emotion_scores.get)
    
    return Emotion(detected_emotion), confidence


def get_emotion_emoji(emotion):
    """Get emoji representation of emotion"""
    emoji_map = {
        Emotion.HAPPY: "😊",
        Emotion.SAD: "😢",
        Emotion.ANGRY: "😠",
        Emotion.ANXIOUS: "😰",
        Emotion.NEUTRAL: "😐"
    }
    return emoji_map.get(emotion, "😐")


def is_strong_emotion(emotion, confidence):
    """Check if emotion is strong enough to warrant special handling"""
    # Consider confidence > 0.4 and not neutral as strong emotion
    return emotion != Emotion.NEUTRAL and confidence > 0.4


def get_empathetic_response(emotion):
    """Get empathetic response prefix for strong emotions"""
    responses = {
        Emotion.HAPPY: "I'm glad to hear you're feeling positive! ",
        Emotion.SAD: "I'm sorry to hear you're feeling down. ",
        Emotion.ANGRY: "I understand you're feeling frustrated. ",
        Emotion.ANXIOUS: "I can sense your concern. ",
        Emotion.NEUTRAL: ""
    }
    return responses.get(emotion, "")
