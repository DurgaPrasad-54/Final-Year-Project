import { FaStethoscope, FaUser, FaCopy, FaCheck, FaVolumeUp } from "react-icons/fa";
import { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { speakText, stopSpeaking } from "../utils/voiceUtils";

export default function Message({ msg }) {
  const [copied, setCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const utteranceRef = useRef(null);
  const isUser = msg.role === "user";

  const formatTime = (timestamp) => {
    if (!timestamp) return "";
    const date = new Date(timestamp);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(msg.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleSpeak = () => {
    if (isSpeaking) {
      stopSpeaking();
      setIsSpeaking(false);
      utteranceRef.current = null;
    } else {
      setIsSpeaking(true);
      utteranceRef.current = speakText(msg.content, "en-US", () => {
        setIsSpeaking(false);
        utteranceRef.current = null;
      });
    }
  };

  return (
    <div className={`message ${isUser ? "user-message" : "assistant-message"}`}>
      <div className="message-avatar">
        {isUser ? <FaUser /> : <FaStethoscope />}
      </div>
      <div className="message-bubble">
        <div className="message-header">
          <div className="message-sender-row">
            <span className="message-sender">{isUser ? "You" : "MedChat AI"}</span>
          </div>
          <div className="message-actions">
            {msg.timestamp && (
              <span className="message-time">{formatTime(msg.timestamp)}</span>
            )}
            {!isUser && (
              <>
                <button 
                  className={`speak-btn ${isSpeaking ? "speaking" : ""}`}
                  onClick={handleSpeak}
                  title={isSpeaking ? "Stop playing" : "Play response"}
                >
                  <FaVolumeUp />
                </button>
                <button 
                  className="copy-btn" 
                  onClick={copyToClipboard}
                  title={copied ? "Copied!" : "Copy response"}
                >
                  {copied ? <FaCheck className="copied" /> : <FaCopy />}
                </button>
              </>
            )}
          </div>
        </div>
        <div className="message-content">
          {isUser ? (
            msg.content
          ) : (
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
              {msg.content}
            </ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  );
}
