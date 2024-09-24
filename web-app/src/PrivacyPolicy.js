// src/PrivacyPolicy.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Page.css';

function PrivacyPolicy() {
  return (
    <div className="page-container">
      <header className="header">
        <div className="header-text">
          <h1>EmailSnap</h1>
        </div>
      </header>

      <div className="page-content">
        <h1>Privacy Policy</h1>

        <p>Last updated: 21.09.2024</p>

        <h2>Introduction</h2>
        <p>
          Welcome to EmailSnap.app ("we", "us", or "our"). We are committed to protecting your personal information and your right to privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you use our service.
        </p>

        <h2>Use at Your Own Risk</h2>
        <p>
          By using EmailSnap.app, you acknowledge and agree that you are using our service at your own risk. While we strive to protect your data, we cannot guarantee absolute security. We recommend that you do not share sensitive or confidential information through our service.
        </p>

        <h2>Data Collection</h2>
        <p>
          We collect personal data that you voluntarily provide to us when you use our service. This includes:
        </p>
        <ul>
          <li>Email addresses</li>
          <li>Email content and attachments you send to us</li>
        </ul>

        <h2>Data Usage</h2>
        <p>
          We use your data to:
        </p>
        <ul>
          <li>Provide and improve our services</li>
          <li>Analyze and summarize email content and attachments</li>
          <li>Communicate with you regarding your use of the service</li>
        </ul>

        <h2>Data Security</h2>
        <p>
          We implement commercially reasonable measures to secure your personal information. However, no method of transmission over the internet or electronic storage is completely secure. Therefore, we cannot guarantee its absolute security.
        </p>

        <h2>Data Sharing</h2>
        <p>
          We do not sell or rent your personal data to third parties. We may share your data with service providers who assist us in operating our service, subject to confidentiality agreements.
        </p>

        <h2>User Responsibilities</h2>
        <p>
          You are responsible for maintaining the confidentiality of any sensitive information. Please refrain from sharing sensitive personal data, confidential business information, or any other information that you do not wish to be processed by our AI systems.
        </p>

        <h2>Children's Privacy</h2>
        <p>
          Our service is not intended for individuals under the age of 18. We do not knowingly collect personal information from children under 18. If we become aware that we have collected such information, we will take steps to delete it.
        </p>

        <h2>Changes to This Privacy Policy</h2>
        <p>
          We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page. We encourage you to review this Privacy Policy periodically for any changes.
        </p>

        <h2>Contact Us</h2>
        <p>
          If you have any questions or concerns about this Privacy Policy, please contact us at:
          <br />
          <a href="mailto:help@emailsnap.app">help@emailsnap.app</a>
        </p>
      </div>

      <footer className="footer">
        <p>
          &copy; {new Date().getFullYear()} EmailSnap. All rights reserved. | Igor Steblii |
          <a href="mailto:help@emailsnap.app" className="footer-link"> help@emailsnap.app</a> |
          <Link to="/privacy-policy" className="footer-link"> Privacy Policy</Link>
        </p>
      </footer>
    </div>
  );
}

export default PrivacyPolicy;
