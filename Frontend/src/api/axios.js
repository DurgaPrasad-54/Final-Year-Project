import axios from "axios";

const API_BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,  // 60 seconds timeout for regular requests (Gemini can take time)
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor - add token to headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors and token expiry
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.clear();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ===== STREAMING SUPPORT FOR REAL-TIME RESPONSES =====

/**
 * Stream chat response using Server-Sent Events
 * @param {string} question - The question to ask
 * @param {string} chatId - Optional chat ID
 * @param {function} onToken - Callback for each token received
 * @param {function} onDone - Callback when streaming is complete
 * @param {function} onError - Callback for errors
 */
export const streamChatResponse = async (question, chatId, onToken, onDone, onError) => {
  const token = localStorage.getItem("access_token");
  
  try {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ question, chatId }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Stream request failed");
    }

    // Check if it's a streaming response or regular JSON
    const contentType = response.headers.get("content-type");
    
    if (contentType && contentType.includes("text/event-stream")) {
      // Handle Server-Sent Events
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let fullResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          if (onDone) onDone(fullResponse);
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE messages
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.token) {
                fullResponse += data.token;
                if (onToken) onToken(data.token, fullResponse);
              }
              
              if (data.done) {
                if (onDone) onDone(fullResponse);
                return;
              }
              
              if (data.error) {
                if (onError) onError(data.error);
                return;
              }
            } catch (parseError) {
              // Skip malformed JSON
            }
          }
        }
      }
    } else {
      // Handle regular JSON response (non-medical questions)
      const data = await response.json();
      if (data.answer) {
        if (onToken) onToken(data.answer, data.answer);
        if (onDone) onDone(data.answer);
      }
    }
  } catch (error) {
    console.error("Stream error:", error);
    if (onError) onError(error.message || "Failed to get response");
  }
};

export default api;
