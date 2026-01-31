import "./sidebar.css";
import { FaTrash, FaPlus, FaSignOutAlt, FaHistory, FaSearch, FaMoon, FaSun, FaBars, FaTimes } from "react-icons/fa";
import { useState, useEffect, forwardRef, useImperativeHandle, useCallback, useMemo } from "react";
import { useTheme } from "../context/ThemeContext";
import api from "../api/axios";

const Sidebar = forwardRef(({ onLoadChat, onNewChat, onClear, onLogout, activeChat }, ref) => {
  const [chats, setChats] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  // Load chats from API
  const loadChats = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get("/chat/list");
      if (res.data && res.data.chats) {
        setChats(res.data.chats);
      }
    } catch (err) {
      console.error("Failed to load chats:", err);
      setChats([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Expose functions to parent component
  useImperativeHandle(ref, () => ({
    loadChats: loadChats
  }), [loadChats]);

  // Load chats on mount
  useEffect(() => {
    loadChats();
  }, [loadChats]);

  // Reload chats when activeChat changes (new message sent)
  useEffect(() => {
    if (activeChat) {
      // Small delay to allow backend to save the message
      const timer = setTimeout(() => {
        loadChats();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [activeChat, loadChats]);

  const handleNewChat = () => {
    onNewChat();
    setSearchTerm("");
    setSidebarOpen(false); // Close sidebar after action on mobile
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  const handleDeleteChat = async (chatId, e) => {
    e.stopPropagation();
    if (window.confirm("Delete this chat?")) {
      try {
        await api.delete(`/chat/delete/${chatId}`);
        // Update local state immediately for faster UI
        setChats(prev => prev.filter(c => c.chatId !== chatId));
        // If the deleted chat is active, trigger new chat
        if (activeChat === chatId) {
          onNewChat();
        }
        closeSidebar(); // Close sidebar after action on mobile
      } catch (err) {
        console.error("Failed to delete chat:", err);
      }
    }
  };

  // Memoized filtered chats for performance
  const filteredChats = useMemo(() => 
    chats.filter(chat =>
      (chat.title || "").toLowerCase().includes(searchTerm.toLowerCase())
    ),
    [chats, searchTerm]
  );

  const truncateText = (text, maxLength = 35) => {
    if (!text) return "Untitled";
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  };

  return (
    <>
      {/* Hamburger menu button - visible only on mobile */}
      <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)} title="Toggle sidebar">
        {sidebarOpen ? <FaTimes /> : <FaBars />}
      </button>

      {/* Sidebar overlay - closes sidebar when clicked on mobile */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={closeSidebar}></div>}

      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`} data-theme={theme}>
      <div className="sidebar-header">
        <div className="sidebar-header-top">
          <h2>MedChat</h2>
          {/* Close button for mobile */}
          <button className="sidebar-close" onClick={closeSidebar} title="Close sidebar">
            <FaTimes />
          </button>
        </div>
        <button className="new-chat-btn" onClick={handleNewChat} title="Start new conversation">
          <FaPlus /> New Chat
        </button>
      </div>

      <div className="search-box">
        <FaSearch className="search-icon" />
        <input
          type="text"
          placeholder="Search chats..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>

      <div className="chats-section">
        <div className="section-title">
          <FaHistory /> Recent Chats
        </div>
        
        {loading ? (
          <div className="loading">Loading chats...</div>
        ) : filteredChats.length === 0 ? (
          <div className="empty-chats">
            {chats.length === 0 ? "No chats yet" : "No matching chats"}
          </div>
        ) : (
          <div className="chats-list">
            {filteredChats.map((chat) => (
              <div
                key={chat.chatId}
                className={`chat-item ${activeChat === chat.chatId ? "active" : ""}`}
                onClick={() => {
                  onLoadChat(chat.chatId);
                  closeSidebar(); // Close sidebar after selecting chat on mobile
                }}
              >
                <div className="chat-text">
                  <p className="chat-title">{truncateText(chat.title)}</p>
                  {(chat.updatedAt || chat.createdAt) && (
                    <p className="chat-time">
                      {new Date(chat.updatedAt || chat.createdAt).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit"
                      })}
                    </p>
                  )}
                </div>
                <button
                  className="delete-btn"
                  onClick={(e) => handleDeleteChat(chat.chatId, e)}
                  title="Delete chat"
                >
                  <FaTrash />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="sidebar-actions">
        <button className="theme-btn" onClick={toggleTheme} title={theme === "light" ? "Switch to Dark Mode" : "Switch to Light Mode"}>
          {theme === "light" ? <FaMoon /> : <FaSun />}
          {theme === "light" ? "Dark Mode" : "Light Mode"}
        </button>
        <button className="clear-btn" onClick={onClear} title="Clear all chats">
          <FaTrash /> Clear All
        </button>
        <button className="logout-btn" onClick={onLogout} title="Logout">
          <FaSignOutAlt /> Logout
        </button>
      </div>
    </aside>
    </>
  );
});

Sidebar.displayName = 'Sidebar';

export default Sidebar;
