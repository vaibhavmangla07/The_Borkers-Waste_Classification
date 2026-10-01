import React from 'react';
import { Link } from 'react-router-dom';
import { Leaf, Shield, Terminal } from 'lucide-react';
import './Footer.css';

export function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-container">
        <div className="footer-brand-section">
          <div className="footer-brand">
            <div className="footer-logo-icon">
              <Leaf size={18} />
            </div>
            <span>EcoVision AI</span>
          </div>
          <p className="footer-tagline">
            Smart Waste Classification & Disposal Intelligence Platform.
            Built for modern municipal recycling compliance.
          </p>
        </div>

        <div className="footer-links-group">
          <div className="footer-col">
            <h5 className="footer-heading">Platform</h5>
            <Link to="/" className="footer-link">Home</Link>
            <Link to="/classify" className="footer-link">Classify Waste</Link>
            <Link to="/categories" className="footer-link">Categories Guide</Link>
          </div>

          <div className="footer-col">
            <h5 className="footer-heading">Intelligence</h5>
            <Link to="/dashboard" className="footer-link">Dashboard</Link>
            <Link to="/history" className="footer-link">Scan History</Link>
            <Link to="/analytics" className="footer-link">Analytics</Link>
          </div>

          <div className="footer-col">
            <h5 className="footer-heading">Architecture</h5>
            <Link to="/about" className="footer-link">System Blueprint</Link>
            <span className="footer-tech-tag">PyTorch Local Engine</span>
            <span className="footer-tech-tag">FastAPI + PostgreSQL</span>
          </div>
        </div>
      </div>

      <div className="container footer-bottom">
        <p className="copyright">
          © 2026 EcoVision AI • Hackathon Edition.
        </p>
        <div className="footer-specs">
          <span className="spec-item"><Shield size={13} /> Zero External AI APIs</span>
          <span className="spec-item"><Terminal size={13} /> Local Inference</span>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
