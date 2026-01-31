import { FaStethoscope, FaUser, FaCopy, FaCheck } from "react-icons/fa";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Message({ msg }) {
  const [copied, setCopied] = useState(false);
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

  return (
    <div className={`message ${isUser ? "user-message" : "assistant-message"}`}>
      <div className="message-avatar">
        {isUser ? <FaUser /> : <FaStethoscope />}
      </div>
      <div className="message-bubble">
        <div className="message-header">
          <span className="message-sender">{isUser ? "You" : "MedChat AI"}</span>
          <div className="message-actions">
            {msg.timestamp && (
              <span className="message-time">{formatTime(msg.timestamp)}</span>
            )}
            {!isUser && (
              <button 
                className="copy-btn" 
                onClick={copyToClipboard}
                title={copied ? "Copied!" : "Copy response"}
              >
                {copied ? <FaCheck className="copied" /> : <FaCopy />}
              </button>
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
