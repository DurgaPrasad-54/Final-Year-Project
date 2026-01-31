import { Link } from "react-router-dom";
import "./footer.css";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h4>MedChat</h4>
          <p>Your trusted AI medical assistant for educational purposes.</p>
        </div>

        <div className="footer-section">
          <h4>Legal</h4>
          <ul>
            <li>
              <Link to="/privacy">Privacy Policy</Link>
            </li>
            <li>
              <Link to="/terms">Terms of Services</Link>
            </li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Contact</h4>
          <ul>
            <li>Email: support@medchat.example.com</li>
            <li>Emergency: 911 (US)</li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; 2026 MedChat. All rights reserved. Not a substitute for professional medical advice.</p>
      </div>
    </footer>
  );
}
