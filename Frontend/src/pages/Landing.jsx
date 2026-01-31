import "./landing.css";
import { Link } from "react-router-dom";
import { FaRobot, FaLock, FaLightbulb, FaClock, FaCheckCircle, FaBars, FaTimes } from "react-icons/fa";
import { useState } from "react";

export default function Landing() {
  const [navOpen, setNavOpen] = useState(false);

  const closeNav = () => {
    setNavOpen(false);
  };
  return (
    <>
      <header className="navbar">
        <div className="nav-container">
          <div className="logo">
            <FaRobot className="logo-icon" />
            <h2>MedChat</h2>
          </div>
          
          {/* Hamburger menu button */}
          <button className="nav-toggle" onClick={() => setNavOpen(!navOpen)} title="Toggle menu">
            {navOpen ? <FaTimes /> : <FaBars />}
          </button>

          {/* Navigation links */}
          <nav className={`nav-links ${navOpen ? "open" : ""}`}>
            <a href="#features" className="nav-link" onClick={closeNav}>Features</a>
            <a href="#about" className="nav-link" onClick={closeNav}>About</a>
            <Link to="/login" className="nav-link" onClick={closeNav}>Login</Link>
            <Link to="/register" className="nav-button" onClick={closeNav}>Sign Up</Link>
          </nav>
        </div>
      </header>

      <section className="hero" id="hero">
        <div className="hero-content">
          <div className="hero-text">
            <h1>Your Trusted <span>AI Medical</span> Assistant</h1>
            <p>Get instant, reliable answers to your health questions. Powered by RAG technology with verified medical knowledge sources.</p>
            <div className="hero-buttons">
              <Link to="/register" className="btn btn-primary btn-large">Get Started Free</Link>
              <Link to="/login" className="btn btn-secondary">Sign In</Link>
            </div>
          </div>
          <div className="hero-image">
            <div className="floating-card">
              <FaRobot className="hero-icon" />
              <p>RAG-Powered AI</p>
              <span>Verified Medical Sources</span>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="features">
        <h2>Why Choose MedChat?</h2>
        <p className="features-subtitle">Built with medical professionals in mind, designed for everyone to use</p>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <FaRobot />
            </div>
            <h3>AI-Powered</h3>
            <p>Advanced AI trained on comprehensive medical knowledge to provide accurate information.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FaLock />
            </div>
            <h3>Secure & Private</h3>
            <p>Your health data is encrypted and kept private. We never share your conversations.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FaClock />
            </div>
            <h3>Available 24/7</h3>
            <p>Get medical information anytime, anywhere. No waiting for appointments.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FaCheckCircle />
            </div>
            <h3>Instant Responses</h3>
            <p>Get instant answers to your medical questions without any delay.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FaLightbulb />
            </div>
            <h3>Evidence-Based</h3>
            <p>Information backed by medical research and clinical expertise.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FaCheckCircle />
            </div>
            <h3>Easy to Use</h3>
            <p>Simple, intuitive interface designed for everyone to use easily.</p>
          </div>
        </div>
      </section>

      <section id="about" className="about">
        <h2>About MedChat</h2>
        <div className="about-content">
          <p>
            MedChat is an advanced AI-powered medical assistant designed to provide quick, accurate, and reliable medical information. Our system leverages cutting-edge natural language processing and medical knowledge bases to help you understand health topics better.
          </p>
          <p>
            Whether you have questions about symptoms, treatments, medications, or general health topics, MedChat is here to help 24/7. While not a replacement for professional medical advice, MedChat serves as a helpful resource for health information and education.
          </p>
          <div className="about-highlights">
            <div className="highlight">
              <h4>Instant Answers</h4>
              <p>Get medical information immediately</p>
            </div>
            <div className="highlight">
              <h4>Comprehensive Coverage</h4>
              <p>Thousands of medical topics covered</p>
            </div>
            <div className="highlight">
              <h4>Always Available</h4>
              <p>Access information anytime you need</p>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <h2>Ready to Get Started?</h2>
        <p>Join thousands of users who trust MedChat for medical information</p>
        <Link to="/register" className="btn btn-primary btn-large">Create Your Account Now</Link>
      </section>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>MedChat</h4>
            <p>Your AI Medical Assistant</p>
          </div>
          <div className="footer-section">
            <h4>Links</h4>
            <ul>
              <li><a href="#features">Features</a></li>
              <li><a href="#about">About</a></li>
              <li><Link to="/login">Login</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Legal</h4>
            <ul>
              <li><Link to="/privacy">Privacy Policy</Link></li>
              <li><Link to="/terms">Terms of Service</Link></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2026 MedChat. All rights reserved.</p>
        </div>
      </footer>
    </>
  );
}
