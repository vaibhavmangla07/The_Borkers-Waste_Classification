import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, Home, ScanLine } from 'lucide-react';

export function NotFound() {
  return (
    <div className="container" style={{ padding: '6rem 1.5rem', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
      <div className="glass-panel" style={{ padding: '3rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.25rem' }}>
        <AlertCircle size={48} style={{ color: 'var(--primary-400)' }} />
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: '#fff' }}>404</h1>
        <h2 style={{ fontSize: '1.25rem', color: 'var(--text-secondary)' }}>Page Not Found</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          The requested route does not exist in EcoVision AI.
        </p>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <Link to="/" className="btn btn-secondary">
            <Home size={16} /> Home
          </Link>
          <Link to="/classify" className="btn btn-primary">
            <ScanLine size={16} /> Classify Waste
          </Link>
        </div>
      </div>
    </div>
  );
}

export default NotFound;
