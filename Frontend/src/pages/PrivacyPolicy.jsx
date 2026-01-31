import "./legal.css";
import { Link } from "react-router-dom";
import { FaArrowLeft } from "react-icons/fa";
import { useEffect } from "react";

export default function PrivacyPolicy() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="legal-page">
      <header className="legal-header">
        <div className="legal-nav">
          <Link to="/" className="back-button">
            <FaArrowLeft /> Back to Home
          </Link>
        </div>
        <h1>Privacy Policy</h1>
        <p className="last-updated">Last updated: January 5, 2026</p>
      </header>

      <main className="legal-content">
        <section>
          <h2>1. Introduction</h2>
          <p>
            MedChat ("we," "us," "our," or "Company") is committed to protecting your privacy. This Privacy Policy 
            explains how we collect, use, disclose, and otherwise handle your information when you use our medical AI 
            chatbot application.
          </p>
        </section>

        <section>
          <h2>2. Information We Collect</h2>
          <p>
            We may collect information about you in a variety of ways. The information we may collect on the Site includes:
          </p>
          <ul>
            <li><strong>Personal Identification Information:</strong> Name, email address, password, phone number (optional)</li>
            <li><strong>Health Information:</strong> Medical queries and health-related questions you submit through the chatbot</li>
            <li><strong>Technical Information:</strong> IP address, browser type, operating system, referring URLs, and pages visited</li>
            <li><strong>Usage Data:</strong> How you interact with our application, including chat history and timestamps</li>
          </ul>
        </section>

        <section>
          <h2>3. How We Use Your Information</h2>
          <p>We use the information we collect in the following ways:</p>
          <ul>
            <li>To provide, maintain, and improve our medical chatbot services</li>
            <li>To personalize your user experience and provide custom-tailored content</li>
            <li>To send periodic emails regarding your account or other important updates</li>
            <li>To improve our website and customer service</li>
            <li>To monitor and analyze usage trends and site performance</li>
            <li>To detect and prevent fraudulent transactions and other illegal activities</li>
          </ul>
        </section>

        <section>
          <h2>4. Health Information and HIPAA Compliance</h2>
          <p>
            MedChat is designed for educational and informational purposes only. While we handle health-related information 
            with the utmost care:
          </p>
          <ul>
            <li>We implement industry-standard encryption and security measures</li>
            <li>Health information is processed securely and not shared with third parties for marketing purposes</li>
            <li>Your medical queries are not used to create profiles for sale or sharing</li>
            <li>We comply with applicable data protection regulations</li>
          </ul>
        </section>

        <section>
          <h2>5. Information Protection</h2>
          <p>
            We implement appropriate technical and organizational measures designed to protect personal information against 
            unauthorized access, alteration, disclosure, or destruction. However, no method of transmission over the Internet 
            or electronic storage is 100% secure.
          </p>
          <p>
            Security measures include:
          </p>
          <ul>
            <li>SSL/TLS encryption for data in transit</li>
            <li>Password protection and authentication mechanisms</li>
            <li>Regular security audits and updates</li>
            <li>Limited access to personal information</li>
          </ul>
        </section>

        <section>
          <h2>6. Third-Party Services</h2>
          <p>
            Our application may use third-party services for authentication, payment processing, and analytics. These 
            third parties have their own privacy policies, and we encourage you to review them. We are not responsible 
            for the privacy practices of third-party services.
          </p>
        </section>

        <section>
          <h2>7. User Rights</h2>
          <p>
            You have the right to:
          </p>
          <ul>
            <li>Access the personal information we hold about you</li>
            <li>Request correction of inaccurate personal information</li>
            <li>Request deletion of your account and associated data</li>
            <li>Opt-out of non-essential communications</li>
            <li>Data portability where applicable</li>
          </ul>
          <p>
            To exercise these rights, please contact us at privacy@medchat.example.com with a clear description of 
            your request.
          </p>
        </section>

        <section>
          <h2>8. Cookies and Tracking Technologies</h2>
          <p>
            We may use cookies and similar tracking technologies to enhance your experience. These include:
          </p>
          <ul>
            <li><strong>Essential Cookies:</strong> Required for authentication and basic functionality</li>
            <li><strong>Analytics Cookies:</strong> Help us understand how you use our application</li>
            <li><strong>Preference Cookies:</strong> Remember your theme and language preferences</li>
          </ul>
          <p>
            You can control cookie settings through your browser preferences. Disabling cookies may affect functionality.
          </p>
        </section>

        <section>
          <h2>9. Medical Disclaimer</h2>
          <p>
            <strong>IMPORTANT:</strong> MedChat is an AI-powered educational tool and NOT a substitute for professional 
            medical advice. The information provided is for informational purposes only and should not be used for 
            self-diagnosis or self-treatment. Always consult with a qualified healthcare professional for medical concerns.
          </p>
        </section>

        <section>
          <h2>10. Data Retention</h2>
          <p>
            We retain your personal information for as long as necessary to provide our services and fulfill the purposes 
            outlined in this policy. You can request deletion of your account and data at any time. Some information may be 
            retained for legal compliance or dispute resolution purposes.
          </p>
        </section>

        <section>
          <h2>11. Children's Privacy</h2>
          <p>
            MedChat is not directed to individuals under the age of 18. We do not knowingly collect personal information 
            from children. If we become aware that we have collected personal information from a child, we will promptly 
            delete such information.
          </p>
        </section>

        <section>
          <h2>12. Changes to This Privacy Policy</h2>
          <p>
            We reserve the right to modify this Privacy Policy at any time. Changes will be effective immediately upon 
            posting to the website. Your continued use of our service constitutes your acceptance of the updated policy.
          </p>
        </section>

        <section>
          <h2>13. Contact Us</h2>
          <p>
            If you have questions about this Privacy Policy or our privacy practices, please contact us at:
          </p>
          <div className="contact-info">
            <p><strong>MedChat Support Team</strong></p>
            <p>Email: prasad8790237@gmail.com</p>
            <p>Address: KIET, Korangi</p>
          </div>
        </section>
      </main>
    </div>
  );
}
