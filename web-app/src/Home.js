// src/Home.js
import React from 'react';
import { FaEnvelopeOpenText, FaFileAlt, FaCloudUploadAlt, FaListAlt } from 'react-icons/fa';
import './Home.css';
import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="home-container">
      <header className="header">
        <div className="header-content">
          <img
            src={`${process.env.PUBLIC_URL}/android-chrome-512x512.png`}
            alt="EmailSnap Logo"
            className="logo-icon"
          />
          <h1>EmailSnap</h1>
        </div>
      </header>

      <section className="intro">
        <p>
          EmailSnap takes your messy inbox and transforms it into a clean, organized powerhouse.
          It's as easy as a snap!
        </p>
      </section>

      <section className="features">
        <div className="feature">
          <FaEnvelopeOpenText className="feature-icon" />
          <h3>Seamless Email Intake</h3>
          <p>
            Incoming emails? We handle them all. EmailSnap grabs your unprocessed emails, ready
            for transformation.
          </p>
        </div>
        <div className="feature">
          <FaFileAlt className="feature-icon" />
          <h3>Attachment Parsing</h3>
          <p>
            Attachments? No problem. We scan, parse, and extract everything from files to images—automatically.
          </p>
        </div>

        <div className="feature">
          <FaCloudUploadAlt className="feature-icon" />
          <h3>Secure Cloud Storage</h3>
          <p>
            Your emails and attachments are stored securely in the cloud with Amazon S3. Accessible whenever you need them.
          </p>
        </div>

        <div className="feature">
          <FaListAlt className="feature-icon" />
          <h3>Powerful Summaries</h3>
          <p>
            No more endless scrolling. Get crisp, AI-powered summaries sent directly to the right person.
          </p>
        </div>
      </section>

       <section className="catchphrase">
        <p>
          <strong>
            Check it out, just forward your email to{' '}
            <a href="mailto:review@emailsnap.app">review@emailsnap.app</a>!
          </strong>
        </p>
      </section>

      <button
        className="try-now-button"
        onClick={() => window.location.href = 'mailto:review@emailsnap.app'}
      >
        TRY NOW
      </button>

      <footer className="footer">
        <p>
          &copy; {new Date().getFullYear()} EmailSnap. All rights reserved. |
          <a href="mailto:help@emailsnap.app" className="footer-link"> help@emailsnap.app</a> |
          <Link to="/privacy-policy" className="footer-link"> Privacy Policy</Link>
        </p>
      </footer>
    </div>
  );
}

export default Home;
