import "./legal.css";
import { Link } from "react-router-dom";
import { FaArrowLeft } from "react-icons/fa";
import { useEffect } from "react";

export default function TermsOfServices() {
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
        <h1>Terms of Services</h1>
        <p className="last-updated">Last updated: January 5, 2026</p>
      </header>

      <main className="legal-content">
        <section>
          <h2>1. Acceptance of Terms</h2>
          <p>
            By accessing and using MedChat ("the Application"), you accept and agree to be bound by the terms and provision 
            of this agreement. If you do not agree to abide by the above, please do not use this service.
          </p>
        </section>

        <section>
          <h2>2. Educational Purpose Only</h2>
          <p>
            <strong>CRITICAL NOTICE:</strong> MedChat is an artificial intelligence tool designed for educational and 
            informational purposes only. It is NOT:
          </p>
          <ul>
            <li>A substitute for professional medical advice, diagnosis, or treatment</li>
            <li>A replacement for consultation with licensed healthcare professionals</li>
            <li>Approved or endorsed by any medical regulatory body</li>
            <li>A medical device as defined by regulatory agencies</li>
          </ul>
          <p>
            <strong>Always consult with a qualified healthcare professional for any medical concerns.</strong>
          </p>
        </section>

        <section>
          <h2>3. User Eligibility</h2>
          <p>
            By using MedChat, you represent and warrant that:
          </p>
          <ul>
            <li>You are at least 18 years of age (or legal age of majority in your jurisdiction)</li>
            <li>You have the legal authority to enter into this agreement</li>
            <li>You will comply with all applicable laws and regulations</li>
            <li>You will not use the service for any unlawful purposes</li>
          </ul>
        </section>

        <section>
          <h2>4. User Responsibilities</h2>
          <p>
            As a user of MedChat, you agree to:
          </p>
          <ul>
            <li>Provide accurate and truthful information when creating an account</li>
            <li>Maintain the confidentiality of your password and account information</li>
            <li>Take responsibility for all activities that occur under your account</li>
            <li>Report any unauthorized use of your account immediately</li>
            <li>Not impersonate any person or entity</li>
            <li>Not transmit any harmful, offensive, or illegal content</li>
            <li>Not attempt to gain unauthorized access to the system</li>
            <li>Not engage in any form of harassment or abuse</li>
          </ul>
        </section>

        <section>
          <h2>5. Limitation of Liability</h2>
          <p>
            <strong>TO THE FULLEST EXTENT PERMITTED BY LAW:</strong>
          </p>
          <ul>
            <li>
              MedChat and its operators shall not be liable for any indirect, incidental, special, consequential, or 
              punitive damages arising from your use or inability to use the service
            </li>
            <li>
              We are not responsible for any harm resulting from actions taken based on information provided by the AI 
              chatbot
            </li>
            <li>
              In no event shall our total liability exceed the amount paid by you for using our service in the past 12 months
            </li>
            <li>
              We are not liable for any medical outcomes, diagnosis errors, or health complications resulting from use 
              of this service
            </li>
          </ul>
        </section>

        <section>
          <h2>6. Medical Liability Disclaimer</h2>
          <p>
            <strong>IMPORTANT MEDICAL DISCLAIMERS:</strong>
          </p>
          <ul>
            <li>
              Any information provided by MedChat is not a diagnosis and should not be relied upon as medical advice
            </li>
            <li>
              In case of medical emergency, call emergency services (911 in the US) immediately
            </li>
            <li>
              The AI may provide inaccurate or outdated medical information despite our best efforts to maintain accuracy
            </li>
            <li>
              You acknowledge and accept all risks associated with relying on AI-generated medical information
            </li>
            <li>
              MedChat is not liable for any misdiagnosis, medical complications, or adverse health outcomes
            </li>
            <li>
              Users are solely responsible for seeking appropriate professional medical care
            </li>
          </ul>
        </section>

        <section>
          <h2>7. Privacy and Data Usage</h2>
          <p>
            Your use of MedChat is also governed by our Privacy Policy. By using this application, you consent to our 
            collection and use of your information as described in the Privacy Policy. Please review our Privacy Policy 
            to understand our practices regarding your health information and personal data.
          </p>
        </section>

        <section>
          <h2>8. Intellectual Property Rights</h2>
          <p>
            All content on MedChat, including but not limited to text, graphics, logos, images, and software, is the 
            property of MedChat or its content suppliers and is protected by international copyright laws. You may not 
            reproduce, distribute, or transmit any content without our prior written consent.
          </p>
        </section>

        <section>
          <h2>9. Third-Party Links</h2>
          <p>
            MedChat may contain links to third-party websites and resources. We are not responsible for the content, 
            accuracy, or practices of external sites. We do not endorse any third-party content and are not liable for 
            any harm resulting from your access to third-party resources.
          </p>
        </section>

        <section>
          <h2>10. No Warranty</h2>
          <p>
            <strong>MedChat is provided "AS IS" without warranty of any kind, express or implied, including but not 
            limited to warranties of merchantability, fitness for a particular purpose, or non-infringement.</strong>
          </p>
          <p>
            We do not guarantee that:
          </p>
          <ul>
            <li>The service will be uninterrupted or error-free</li>
            <li>Any defects will be corrected</li>
            <li>Information will be accurate or complete</li>
            <li>The service will meet your specific requirements</li>
          </ul>
        </section>

        <section>
          <h2>11. Account Termination</h2>
          <p>
            We reserve the right to suspend or terminate your account and access to MedChat if:
          </p>
          <ul>
            <li>You violate any provision of this agreement</li>
            <li>You engage in illegal or harmful activities</li>
            <li>We receive complaints about your conduct</li>
            <li>We determine your account poses a security risk</li>
          </ul>
          <p>
            Termination will not relieve you of any obligations incurred during the use of the service.
          </p>
        </section>

        <section>
          <h2>12. Modifications to Terms</h2>
          <p>
            We reserve the right to modify these Terms of Service at any time. Changes will be effective upon posting 
            to the website. Your continued use of MedChat after any modifications indicates your acceptance of the new terms.
          </p>
        </section>

        <section>
          <h2>13. Severability</h2>
          <p>
            If any provision of these Terms of Service is found to be invalid or unenforceable, the remaining provisions 
            shall continue in full force and effect.
          </p>
        </section>

        <section>
          <h2>14. Governing Law</h2>
          <p>
            These Terms of Service are governed by and construed in accordance with the laws of [Your Jurisdiction], 
            and you irrevocably submit to the exclusive jurisdiction of the courts located in that jurisdiction.
          </p>
        </section>

        <section>
          <h2>15. Contact Information</h2>
          <p>
            If you have any questions about these Terms of Service, please contact us at:
          </p>
          <div className="contact-info">
            <p><strong>MedChat Legal Team</strong></p>
            <p>Email: legal@medchat.example.com</p>
            <p>Address: [Your Address Here]</p>
          </div>
        </section>

        <section className="acceptance-section">
          <h2>16. Your Acceptance</h2>
          <p>
            By accessing and using MedChat, you acknowledge that you have read, understood, and agree to be bound by 
            all the terms and conditions contained herein. If you do not agree to these terms, you should not use this 
            service.
          </p>
        </section>
      </main>
    </div>
  );
}
