/**
 * Voice utilities for Web Speech API
 * Handles both speech recognition (input) and speech synthesis (output)
 */

/**
 * Initialize speech recognition with specified language
 */
export const initializeSpeechRecognition = (language = "en-US") => {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.error(
      "Speech Recognition API not supported in this browser"
    );
    return null;
  }

  const recognition = new SpeechRecognition();
  recognition.language = language;
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  return recognition;
};

/**
 * Start listening for voice input
 * @param {Object} callbacks - {onStart, onResult, onError, onEnd}
 * @param {SpeechRecognition} recognition - Voice recognition instance
 */
export const startListening = (callbacks, recognition) => {
  if (!recognition) return;

  recognition.onstart = () => {
    callbacks.onStart?.();
  };

  recognition.onresult = (event) => {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    callbacks.onResult?.(transcript);
  };

  recognition.onerror = (event) => {
    callbacks.onError?.(event.error);
  };

  recognition.onend = () => {
    callbacks.onEnd?.();
  };

  try {
    recognition.start();
  } catch (error) {
    console.error("Error starting speech recognition:", error);
  }
};

/**
 * Stop listening for voice input
 * @param {SpeechRecognition} recognition - Voice recognition instance
 */
export const stopListening = (recognition) => {
  if (!recognition) return;
  try {
    recognition.abort();
  } catch (error) {
    console.error("Error stopping speech recognition:", error);
  }
};

/**
 * Check if browser supports speech synthesis
 */
export const isSpeechSynthesisSupported = () => {
  return "speechSynthesis" in window;
};

/**
 * Speak text using Web Speech API
 * @param {string} text - Text to speak
 * @param {string} language - Language code (en-US, hi-IN, te-IN)
 * @param {Function} onEnd - Callback when speech ends
 */
export const speakText = (text, language = "en-US", onEnd = null) => {
  if (!isSpeechSynthesisSupported()) {
    console.error("Speech Synthesis API not supported");
    return null;
  }

  // Cancel any ongoing speech
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = language;
  utterance.rate = 1;
  utterance.pitch = 1;
  utterance.volume = 1;

  if (onEnd) {
    utterance.onend = onEnd;
    utterance.onerror = (error) => {
      console.error("Speech synthesis error:", error);
      onEnd();
    };
  }

  window.speechSynthesis.speak(utterance);
  return utterance;
};

/**
 * Stop speech synthesis
 */
export const stopSpeaking = () => {
  if (isSpeechSynthesisSupported()) {
    window.speechSynthesis.cancel();
  }
};

/**
 * Get available voices for a language
 */
export const getAvailableVoices = () => {
  if (!isSpeechSynthesisSupported()) return [];
  return window.speechSynthesis.getVoices();
};

/**
 * Language options for voice
 */
export const LANGUAGE_OPTIONS = [
  { code: "en-US", name: "English (US)" },
  { code: "hi-IN", name: "Hindi (India)" },
  { code: "te-IN", name: "Telugu (India)" },
];
