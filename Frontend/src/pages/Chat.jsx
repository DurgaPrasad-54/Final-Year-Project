import "./chat.css";
import { useEffect, useState, useRef, useCallback } from "react";
import api, { streamChatResponse } from "../api/axios";
import Sidebar from "../components/Sidebar";
import Message from "../components/Message";
import { FaPaperPlane, FaSpinner, FaRobot } from "react-icons/fa";
import { useTheme } from "../context/ThemeContext";
import ReactMarkdown from "react-markdown";

export default function Chat() {
  const { theme } = useTheme();
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState("");
  const [chatId, setChatId] = useState(null);
  const [streamingContent, setStreamingContent] = useState("");
  const messagesEndRef = useRef(null);
  const sidebarRef = useRef(null);

  useEffect(() => {
    // Initialize with new chat on mount
    createNewChat();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const createNewChat = async () => {
    try {
      setError("");
      const res = await api.post("/chat/new");
      if (res.data && res.data.chatId) {
        setChatId(res.data.chatId);
        setMessages([]);
        setStreamingContent("");
      } else {
        throw new Error("No chatId in response");
      }
    } catch (err) {
      console.error("Failed to create new chat:", err);
      setError("Failed to create new chat. Please reload the page.");
    }
  };

  const loadChatById = async (targetChatId) => {
    if (!targetChatId) return;
    
    try {
      setError("");
      setLoading(true);
      setStreamingContent("");
      
      const res = await api.get(`/chat/history?chatId=${targetChatId}`);
      if (res.data && res.data.messages) {
        setMessages(res.data.messages);
        setChatId(targetChatId);
      } else {
        setMessages([]);
        setChatId(targetChatId);
      }
    } catch (err) {
      console.error("Failed to load chat:", err);
      setError("Failed to load chat history");
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  // Refresh sidebar chats list with a small delay to allow backend to save
  const refreshSidebar = useCallback(() => {
    // Small delay to ensure backend has saved the message
    setTimeout(() => {
      if (sidebarRef.current && sidebarRef.current.loadChats) {
        sidebarRef.current.loadChats();
      }
    }, 300);
  }, []);

  const send = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading || streaming) return;

    const userMessage = { role: "user", content: question };
    setMessages(prev => [...prev, userMessage]);
    const currentQuestion = question;
    setQuestion("");
    setError("");
    setStreamingContent("");

    // Try streaming first for real-time response like ChatGPT
    try {
      setStreaming(true);
      
      await streamChatResponse(
        currentQuestion,
        chatId,
        // onToken - called for each new token
        (token, fullResponse) => {
          setStreamingContent(fullResponse);
        },
        // onDone - called when streaming is complete
        (finalResponse) => {
          const assistantMessage = {
            role: "assistant",
            content: finalResponse,
            timestamp: new Date().toISOString()
          };
          setMessages(prev => [...prev, assistantMessage]);
          setStreamingContent("");
          setStreaming(false);
          
          // Refresh sidebar to show updated chat with delay
          refreshSidebar();
        },
        // onError - called on error, fallback to regular API
        async (errorMsg) => {
          console.warn("Streaming failed, falling back to regular API:", errorMsg);
          setStreaming(false);
          setStreamingContent("");
          
          // Fallback to regular API
          await sendRegular(currentQuestion, userMessage);
        }
      );
    } catch (streamError) {
      console.error("Stream error:", streamError);
      setStreaming(false);
      setStreamingContent("");
      
      // Fallback to regular API
      await sendRegular(currentQuestion, userMessage);
    }
  };

  // Regular (non-streaming) send function as fallback
  const sendRegular = async (currentQuestion, userMessage) => {
    setLoading(true);
    try {
      const res = await api.post("/chat/ask", { 
        question: currentQuestion,
        chatId
      });
      
      if (res.data && res.data.answer) {
        if (res.data.chatId && !chatId) {
          setChatId(res.data.chatId);
        }

        const assistantMessage = {
          role: "assistant",
          content: res.data.answer,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, assistantMessage]);

        if (res.data.medical === false) {
          setError("Please ask medical questions for better assistance.");
        }
        
        // Refresh sidebar
        refreshSidebar();
      }
    } catch (err) {
      console.error("Failed to send message:", err);
      
      if (err.code === "ECONNABORTED" || err.message?.includes("timeout")) {
        setError("Request timeout - Please try again.");
      } else if (err.code === "ECONNREFUSED") {
        setError("Connection refused - Backend is not running.");
      } else if (!err.response) {
        setError("Network error - Cannot connect to backend.");
      } else {
        setError(err.response?.data?.error || "Failed to get response.");
      }
      
      // Remove the user message if there was an error
      setMessages(prev => prev.filter(m => m !== userMessage));
    } finally {
      setLoading(false);
    }
  };

  const clearAllChats = async () => {
    if (window.confirm("Are you sure you want to delete all chats? This cannot be undone.")) {
      try {
        try {
          await api.delete("/chat/clear-all");
        } catch (err) {
          await api.delete("/chat/clear");
        }
        setMessages([]);
        setChatId(null);
        setError("");
        setStreamingContent("");
        await createNewChat();
        refreshSidebar();
      } catch (err) {
        console.error("Failed to clear chats:", err);
        setError("Failed to clear chats");
      }
    }
  };

  const logout = () => {
    localStorage.clear();
    window.location.href = "/";
  };

  return (
    <div className="chat-layout" data-theme={theme}>
      <Sidebar 
        ref={sidebarRef}
        onLoadChat={loadChatById}
        onNewChat={createNewChat}
        onClear={clearAllChats}
        onLogout={logout}
        activeChat={chatId}
      />

      <main className="chat-main">
        <div className="chat-header">
          <h1>Medical ChatBot</h1>
          <p>AI-powered assistant with RAG-based trusted sources</p>
        </div>

        <div className="messages-container">
          {messages.length === 0 && !streamingContent ? (
            <div className="empty-state">
              <div className="empty-icon"><FaRobot /></div>
              <h2>Welcome to Medical ChatBot</h2>
              <p>Ask any medical or health-related question and get instant answers powered by AI</p>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <Message key={idx} msg={msg} />
              ))}
              
              {/* Streaming response - shows real-time typing like ChatGPT */}
              {streaming && streamingContent && (
                <div className="message assistant-message streaming">
                  <div className="message-avatar">
                    <FaRobot />
                  </div>
                  <div className="message-bubble">
                    <div className="message-header">
                      <span className="message-sender">MedBot</span>
                    </div>
                    <div className="message-content">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="md-paragraph">{children}</p>,
                          ul: ({ children }) => <ul className="md-list">{children}</ul>,
                          ol: ({ children }) => <ol className="md-list md-ordered">{children}</ol>,
                          li: ({ children }) => <li className="md-list-item">{children}</li>,
                          strong: ({ children }) => <strong className="md-bold">{children}</strong>,
                          em: ({ children }) => <em className="md-italic">{children}</em>,
                          code: ({ children }) => <code className="md-code">{children}</code>,
                          h1: ({ children }) => <h3 className="md-heading">{children}</h3>,
                          h2: ({ children }) => <h4 className="md-heading">{children}</h4>,
                          h3: ({ children }) => <h5 className="md-heading">{children}</h5>,
                        }}
                      >
                        {streamingContent}
                      </ReactMarkdown>
                      <span className="typing-cursor">|</span>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Loading indicator when waiting for response */}
              {(loading || (streaming && !streamingContent)) && (
                <div className="message assistant-message">
                  <div className="message-avatar">
                    <FaRobot />
                  </div>
                  <div className="message-bubble">
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button onClick={() => setError("")}>&times;</button>
          </div>
        )}

        {/* <div className="chat-disclaimer">
          <span className="disclaimer-icon">⚕️</span>
          <p>This AI assistant provides general health information only. Always consult a qualified healthcare professional for medical advice.</p>
        </div> */}

        <form onSubmit={send} className="input-box">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a medical question..."
            disabled={loading || streaming}
            autoFocus
          />
          <button 
            type="submit" 
            disabled={loading || streaming || !question.trim()}
            className="send-button"
          >
            {(loading || streaming) ? (
              <FaSpinner className="spinner" />
            ) : (
              <FaPaperPlane />
            )}
          </button>
        </form>
      </main>
    </div>
  );
}
