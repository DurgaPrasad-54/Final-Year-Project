"""
Translation service for multilingual support
Handles translation of bot responses to Hindi (hi), Telugu (te), and English (en)
"""

import logging

logger = logging.getLogger(__name__)

# Language codes mapping
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu"
}

# Dictionary of common medical terms and phrases in English, Hindi, and Telugu
TRANSLATION_DICT = {
    # Common medical terms
    "symptom*": {
        "en": "symptom",
        "hi": "लक्षण",
        "te": "లక్షణం"
    },
    "treatment*": {
        "en": "treatment",
        "hi": "इलाज",
        "te": "చికిత్స"
    },
    "disease*": {
        "en": "disease",
        "hi": "रोग",
        "te": "వ్యాధి"
    },
    "fever*": {
        "en": "fever",
        "hi": "बुखार",
        "te": "జ్వరం"
    },
    "pain*": {
        "en": "pain",
        "hi": "दर्द",
        "te": "నొప్పి"
    },
    "headache*": {
        "en": "headache",
        "hi": "सिरदर्द",
        "te": "తల నొప్పి"
    },
    "cold*": {
        "en": "cold",
        "hi": "सर्दी",
        "te": "జలుబు"
    },
    "cough*": {
        "en": "cough",
        "hi": "खांसी",
        "te": "దగ్గు"
    },
    "medication*": {
        "en": "medication",
        "hi": "दवा",
        "te": "ఔషధం"
    },
    "doctor*": {
        "en": "doctor",
        "hi": "डॉक्टर",
        "te": "డాక్టర్"
    },
    "hospital*": {
        "en": "hospital",
        "hi": "अस्पताल",
        "te": "ఆసుపత్రి"
    },
    "patient*": {
        "en": "patient",
        "hi": "रोगी",
        "te": "రోగి"
    },
    "health*": {
        "en": "health",
        "hi": "स्वास्थ्य",
        "te": "ఆరోగ్యం"
    },
    "breathing*": {
        "en": "breathing",
        "hi": "साँस लेना",
        "te": "శ్వాస"
    },
    "allergy*": {
        "en": "allergy",
        "hi": "एलर्जी",
        "te": "నిమ్మకులు"
    },
    "infection*": {
        "en": "infection",
        "hi": "संक्रमण",
        "te": "సంక్రమణ"
    },
    "vaccine*": {
        "en": "vaccine",
        "hi": "वैक्सीन",
        "te": "వ్యాక్సిన్"
    },
    "blood*": {
        "en": "blood",
        "hi": "रक्त",
        "te": "రక్తం"
    },
    "heart*": {
        "en": "heart",
        "hi": "हृदय",
        "te": "గుండె"
    },
    "pressure*": {
        "en": "pressure",
        "hi": "दबाव",
        "te": "పీడన"
    },
    "blood pressure*": {
        "en": "blood pressure",
        "hi": "रक्तचाप",
        "te": "రక్తతాపం"
    },
    
    # Common responses
    "i understand*": {
        "en": "I understand",
        "hi": "मैं समझता हूँ",
        "te": "నేను అర్థం చేసుకున్నాను"
    },
    "please*": {
        "en": "please",
        "hi": "कृपया",
        "te": "దయచేసి"
    },
    "thank*": {
        "en": "thank",
        "hi": "धन्यवाद",
        "te": "ధన్యవాదాలు"
    },
    "sorry*": {
        "en": "sorry",
        "hi": "खेद है",
        "te": "క్షమించండి"
    },
    "hello*": {
        "en": "hello",
        "hi": "नमस्ते",
        "te": "హలో"
    },
    "goodbye*": {
        "en": "goodbye",
        "hi": "अलविदा",
        "te": "లేచివెళ్ళండి"
    },
    "help*": {
        "en": "help",
        "hi": "मदद",
        "te": "సహాయం"
    },
    "consult*": {
        "en": "consult",
        "hi": "परामर्श",
        "te": "సలహా"
    },
    "treat*": {
        "en": "treat",
        "hi": "उपचार",
        "te": "చికిత్స"
    },
    "recommend*": {
        "en": "recommend",
        "hi": "अनुशंसा करते हैं",
        "te": "సిఫారసు చేస్తున్నాము"
    }
}

# Complete sentence translations for common responses
RESPONSE_TRANSLATIONS = {
    "greeting": {
        "en": "Hello! I'm MedChat, your medical assistant. How can I help you today?",
        "hi": "नमस्ते! मैं MedChat हूँ, आपका चिकित्सा सहायक। मैं आज आपकी कैसे मदद कर सकता हूँ?",
        "te": "హలో! నేను MedChat, మీ వైద్య సహాయక। నేను ఈ రోజు మీకు ఎలా సహాయం చేయగలను?"
    },
    "thank_you": {
        "en": "You're welcome! Feel free to ask me anything about your health.",
        "hi": "आपका स्वागत है! स्वास्थ्य के बारे में मुझसे कुछ भी पूछने में बेझिझक महसूस करें।",
        "te": "స్వాగతం! మీ ఆరోగ్యం గురించి నన్ను ఏమైనా అడగడానికి నిశ్చింతగా భావించండి."
    },
    "goodbye": {
        "en": "Goodbye! Take care of your health. Feel free to come back if you have more questions.",
        "hi": "अलविदा! अपने स्वास्थ्य का ध्यान रखें। यदि आपके पास और सवाल हों तो वापस आने में बेझिझक महसूस करें।",
        "te": "లేచివెళ్ళండి! మీ ఆరోగ్యం కాపాడండి. మీకు మరిన్ని ప్రశ్నలు ఉంటే తిరిగి రావడానికి నిశ్చింతగా భావించండి."
    },
    "medical_question_required": {
        "en": "Please ask a medical question. I'm here to help with health-related information.",
        "hi": "कृपया एक चिकित्सा प्रश्न पूछें। मैं स्वास्थ्य से संबंधित जानकारी में मदद करने के लिए यहाँ हूँ।",
        "te": "దయచేసి వైద్య ప్రశ్న అడగండి. నేను ఆరోగ్య సంబంధిత సమాచారంలో సహాయం చేయడానికి ఇక్కడ ఉన్నాను."
    },
    "provide_more_details": {
        "en": "Could you please provide more details or rephrase your question? I'm here to help with medical information.",
        "hi": "क्या आप कृपया अधिक विवरण प्रदान कर सकते हैं या अपने प्रश्न को फिर से तैयार कर सकते हैं? मैं चिकित्सा जानकारी में मदद करने के लिए यहाँ हूँ।",
        "te": "దయచేసి మరిన్ని వివరాలను అందించవచ్చు లేదా మీ ప్రశ్నను పున: సూచించవచ్చు? నేను వైద్య సమాచారంలో సహాయం చేయడానికి ఇక్కడ ఉన్నాను."
    },
    "identity": {
        "en": "I'm MedChat, your AI medical assistant. I'm here to provide health information and support.",
        "hi": "मैं MedChat हूँ, आपका एआई चिकित्सा सहायक। मैं स्वास्थ्य जानकारी और समर्थन प्रदान करने के लिए यहाँ हूँ।",
        "te": "నేను MedChat, మీ AI వైద్య సహాయక. నేను ఆరోగ్య సమాచారం మరియు సపోర్టు అందించడానికి ఇక్కడ ఉన్నాను."
    },
    "non_medical": {
        "en": "I'm specialized in medical assistance. Please ask me health-related questions.",
        "hi": "मैं चिकित्सा सहायता में विशेषज्ञ हूँ। कृपया मुझसे स्वास्थ्य से संबंधित प्रश्न पूछें।",
        "te": "నేను వైద్య సహాయంలో నిపుణుడిని. దయచేసి నన్ను ఆరోగ్య సంబంధిత ప్రశ్నలు అడగండి."
    }
}

# Empathetic response translations for emotions
EMPATHETIC_RESPONSES = {
    "happy": {
        "en": "That's great to hear! ",
        "hi": "यह सुनकर खुशी हुई! ",
        "te": "ఇది విన్న సంతోషం! "
    },
    "sad": {
        "en": "I understand this is difficult. ",
        "hi": "मैं समझता हूँ कि यह कठिन है। ",
        "te": "ఇది కష్టమని నేను అర్థం చేసుకున్నాను. "
    },
    "angry": {
        "en": "I completely understand your frustration. ",
        "hi": "मैं आपकी निराशा को पूरी तरह समझ्ता हूँ। ",
        "te": "నీ నిరాశను నేను పూర్తిగా అర్థం చేసుకున్నాను. "
    },
    "anxious": {
        "en": "I can see you're concerned. ",
        "hi": "मैं देख सकता हूँ कि आप चिंतित हैं। ",
        "te": "మీరు చింతిస్తున్నట్లు నేను చూడవచ్చు. "
    },
    "neutral": {
        "en": "Let me help you with that. ",
        "hi": "मुझे आपकी इस मदद करने दीजिए। ",
        "te": "నేను దానిలో మీకు సహాయం చేయనివ్వండి. "
    }
}


def translate_response(text, target_language="en"):
    """
    Translate response text to target language
    
    Args:
        text (str): Original response text in English
        target_language (str): Target language code ('en', 'hi', 'te')
    
    Returns:
        str: Translated text or original if translation not available
    """
    if target_language not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language: {target_language}, returning English")
        return text
    
    if target_language == "en":
        return text
    
    # Check if exact translation exists in response translations
    for key, translations in RESPONSE_TRANSLATIONS.items():
        if text == translations.get("en"):
            return translations.get(target_language, text)
    
    # For longer texts, try to translate key terms and phrases
    translated_text = text
    
    # Replace common terms - simple approach for now
    for english_term, translations in TRANSLATION_DICT.items():
        # Create regex pattern from dictionary key (without the *)
        search_term = english_term.rstrip("*")
        if search_term.lower() in text.lower():
            # Simple word replacement (case-insensitive)
            import re
            pattern = re.compile(r'\b' + re.escape(search_term) + r'\b', re.IGNORECASE)
            replacement = translations.get(target_language, search_term)
            translated_text = pattern.sub(replacement, translated_text)
    
    return translated_text


def get_translated_greeting(target_language="en"):
    """Get greeting in target language"""
    return RESPONSE_TRANSLATIONS.get("greeting", {}).get(
        target_language, 
        RESPONSE_TRANSLATIONS["greeting"]["en"]
    )


def get_translated_farewell(target_language="en"):
    """Get farewell message in target language"""
    return RESPONSE_TRANSLATIONS.get("goodbye", {}).get(
        target_language,
        RESPONSE_TRANSLATIONS["goodbye"]["en"]
    )


def get_translated_empathetic(emotion, target_language="en"):
    """Get empathetic response for emotion in target language"""
    emotion_key = emotion.lower() if isinstance(emotion, str) else emotion.value.lower()
    return EMPATHETIC_RESPONSES.get(emotion_key, {}).get(
        target_language,
        EMPATHETIC_RESPONSES.get(emotion_key, {}).get("en")
    )


def get_supported_languages():
    """Return list of supported language codes"""
    return list(SUPPORTED_LANGUAGES.keys())


def get_language_name(language_code):
    """Get human-readable language name"""
    return SUPPORTED_LANGUAGES.get(language_code, "Unknown")
